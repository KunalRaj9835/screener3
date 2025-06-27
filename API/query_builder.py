"""Enhanced SQL Query Builder for Stock Screener with Multi-Timeframe Support"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from models import (
    SimpleFilter, TemplateFilter, SortConfig, PaginationConfig, 
    FundamentalsFilter, MultiTimeframeFilter, TimeframeEnum
)
from config import OPERATORS, AVAILABLE_FIELDS, TIMEFRAME_TABLE_MAP, TIMEFRAME_INDICATORS_MAP, FUNDAMENTALS_FIELDS
from filter_templates import get_template_manager

logger = logging.getLogger(__name__)

def convert_symbol_yahoo_to_nse(yahoo_symbol: str) -> str:
    """Convert Yahoo Finance symbol format to NSE format
    
    Examples:
        ADANIENT.NS -> NSE:ADANIENT-EQ
        SBIN.NS -> NSE:SBIN-EQ
    """
    if yahoo_symbol.endswith('.NS'):
        base_symbol = yahoo_symbol[:-3]  # Remove .NS
        return f"NSE:{base_symbol}-EQ"
    return yahoo_symbol

def convert_symbol_nse_to_yahoo(nse_symbol: str) -> str:
    """Convert NSE symbol format to Yahoo Finance format
    
    Examples:
        NSE:ADANIENT-EQ -> ADANIENT.NS
        NSE:SBIN-EQ -> SBIN.NS
    """
    if nse_symbol.startswith('NSE:') and nse_symbol.endswith('-EQ'):
        base_symbol = nse_symbol[4:-3]  # Remove NSE: and -EQ
        return f"{base_symbol}.NS"
    return nse_symbol

def get_symbol_conversion_clause() -> str:
    """Get SQL clause to convert between symbol formats for fundamentals join"""
    return "c.symbol = f.symbol"

class ExpressionParser:
    """Parses and validates expression-based filters"""
    
    def __init__(self):
        # Allowed functions in expressions
        self.allowed_functions = {
            'ABS', 'ROUND', 'GREATEST', 'LEAST', 'COALESCE', 'LAG', 'LEAD'
        }
        
        # Allowed SQL logical operators and keywords
        self.allowed_sql_keywords = {
            'AND', 'OR', 'NOT', 'IS', 'NULL', 'BETWEEN', 'IN', 'LIKE', 
            'TRUE', 'FALSE', 'CASE', 'WHEN', 'THEN', 'ELSE', 'END'
        }
        
        # Pattern to match field references
        self.field_pattern = re.compile(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b')
        
        # Pattern to match potentially dangerous keywords
        self.dangerous_keywords = {
            'DROP', 'DELETE', 'INSERT', 'UPDATE', 'CREATE', 'ALTER', 
            'TRUNCATE', 'EXEC', 'EXECUTE', 'UNION', 'DECLARE'
        }
    
    def validate_expression(self, expression: str) -> str:
        """Validate and sanitize an expression"""
        if not expression or not expression.strip():
            raise ValueError("Expression cannot be empty")
        
        # Check for dangerous keywords
        upper_expr = expression.upper()
        for keyword in self.dangerous_keywords:
            if keyword in upper_expr:
                raise ValueError(f"Dangerous keyword '{keyword}' not allowed in expressions")
        
        # Extract all field references
        fields = self.field_pattern.findall(expression)
        
        # Validate that all fields exist
        for field in fields:
            if field.upper() not in [f.upper() for f in self.allowed_functions]:
                if field.upper() not in self.allowed_sql_keywords:
                    if field not in AVAILABLE_FIELDS:
                        raise ValueError(f"Unknown field '{field}' in expression")
        
        return expression.strip()

class MultiTimeframeQueryBuilder:
    """Enhanced Query Builder with multi-timeframe and fundamentals support"""
    
    def __init__(self, primary_timeframe: Union[str, List[str]]):
        if isinstance(primary_timeframe, list):
            self.primary_timeframe = primary_timeframe[0]
            self.additional_timeframes = primary_timeframe[1:]
        else:
            self.primary_timeframe = primary_timeframe
            self.additional_timeframes = []
        
        self.indicators_timeframe = TIMEFRAME_INDICATORS_MAP.get(self.primary_timeframe, self.primary_timeframe)
        self.primary_table = TIMEFRAME_TABLE_MAP.get(self.primary_timeframe)
        
        if not self.primary_table:
            raise ValueError(f"Invalid primary timeframe: {self.primary_timeframe}")
        
        self.expression_parser = ExpressionParser()
        self.template_manager = get_template_manager()
        
    def build_base_query_with_fundamentals(self, include_fundamentals: bool = True, include_latest_only: bool = True) -> str:
        """Build enhanced base query with fundamentals and multi-timeframe support"""
        
        # Base indicators selection
        indicators_select = """
            i.sma_9, i.sma_21, i.sma_50, i.sma_100, i.sma_200,
            i.ema_9, i.ema_21, i.ema_50, i.ema_100, i.ema_200,
            i.wma_9, i.wma_21, i.wma_50, i.wma_100, i.wma_200,
            i.hma_9, i.hma_21, i.hma_50, i.hma_100,
            i.rsi_7, i.rsi_14, i.rsi_21,
            i.macd_12_26_9, i.macd_signal_12_26_9, i.macd_hist_12_26_9,
            i.stochastic_k_14_3_3, i.stochastic_d_14_3_3,
            i.stochastic_k_9_3_3, i.stochastic_d_9_3_3,
            i.atr_14, i.cci_14, i.willr_14, i.roc_14, i.ao_5_34,
            i.obv, i.vwap, i.mfi_14, i.cmf_20,
            i.volume_osc_14_28, i.volume_sma_20,
            i.plus_di_14, i.minus_di_14, i.adx_14,
            i.bb_upper_20_2, i.bb_mid_20_2, i.bb_lower_20_2,
            i.keltner_upper_20_2, i.keltner_mid_20, i.keltner_lower_20_2,
            i.donchian_upper_20, i.donchian_lower_20,
            i.stddev_20, i.pivot, i.pivot_r1, i.pivot_s1, i.pivot_r2, i.pivot_s2,
            i.ichimoku_tenkan_sen, i.ichimoku_kijun_sen, 
            i.ichimoku_senkou_span_a, i.ichimoku_senkou_span_b, i.ichimoku_chikou_span,
            i.supertrend_10_3, i.supertrend_14_2,
            i.tema_20, i.tema_50, i.tema_100
        """
        
        # Fundamentals selection
        fundamentals_select = ""
        if include_fundamentals:
            fundamentals_select = """,
            f.market_cap, f.enterprise_value, f.trailing_pe, f.forward_pe, f.peg_ratio,
            f.price_to_book, f.price_to_sales, f.enterprise_to_revenue, f.enterprise_to_ebitda,
            f.roe, f.roa, f.gross_margin, f.operating_margin, f.profit_margin, f.ebitda_margin,
            f.free_cash_flow, f.operating_cash_flow, f.debt_to_equity, f.current_ratio,
            f.total_debt, f.total_cash, f.revenue_growth, f.earnings_growth,
            f.quarterly_revenue_growth, f.quarterly_earnings_growth, f.dividend_yield,
            f.dividend_rate, f.payout_ratio, f.insider_holding, f.institutional_holding,
            f.float_shares, f.shares_outstanding, f.beta, f.short_ratio,
            f.short_percent_of_float, f.previous_close, f.fifty_day_avg, f.two_hundred_day_avg,
            f.current_price, f.updated_at"""
        
        # Base query
        base_query = f"""
        SELECT 
            c.symbol,
            c.datetime,
            c.open,
            c.high,
            c.low,
            c.close,
            c.volume,
            '{self.primary_timeframe}' as primary_timeframe,
            {indicators_select}
            {fundamentals_select}
        FROM {self.primary_table} c
        JOIN indicators i ON c.datetime = i.datetime 
            AND c.symbol = i.symbol 
            AND i.timeframe = %s
        """
        
        # Add fundamentals join if requested
        if include_fundamentals:
            conversion_clause = get_symbol_conversion_clause()
            base_query += f"""
        LEFT JOIN fundamentals f ON {conversion_clause}
            """
        
        # Add latest data constraint
        if include_latest_only:
            base_query += f"""
            WHERE c.datetime = (
                SELECT MAX(datetime) FROM {self.primary_table}
            )
            """
        
        return base_query
    
    def build_multi_timeframe_condition(self, multi_filter: MultiTimeframeFilter) -> Tuple[str, List]:
        """Build condition for multi-timeframe filters"""
        conditions = []
        params = []
        
        for condition in multi_filter.conditions:
            timeframe = condition.timeframe.value if condition.timeframe else self.primary_timeframe
            table_name = TIMEFRAME_TABLE_MAP.get(timeframe)
            indicators_tf = TIMEFRAME_INDICATORS_MAP.get(timeframe, timeframe)
            
            if not table_name:
                raise ValueError(f"Invalid timeframe in multi-timeframe filter: {timeframe}")
            
            # Build subquery for this specific timeframe
            field = condition.field
            operator = condition.operator
            value = condition.value
            
            if field not in AVAILABLE_FIELDS:
                raise ValueError(f"Unknown field: {field}")
            
            field_info = AVAILABLE_FIELDS[field]
            
            if field_info["table"] == "candles":
                field_ref = f"mt_{timeframe}.{field}"
                subquery = f"""
                EXISTS (
                    SELECT 1 FROM {table_name} mt_{timeframe}
                    WHERE mt_{timeframe}.symbol = c.symbol
                    AND mt_{timeframe}.datetime = (SELECT MAX(datetime) FROM {table_name})
                """
            elif field_info["table"] == "indicators":
                field_ref = f"mti_{timeframe}.{field}"
                subquery = f"""
                EXISTS (
                    SELECT 1 FROM indicators mti_{timeframe}
                    WHERE mti_{timeframe}.symbol = c.symbol
                    AND mti_{timeframe}.timeframe = %s
                    AND mti_{timeframe}.datetime = (
                        SELECT MAX(datetime) FROM indicators 
                        WHERE symbol = c.symbol AND timeframe = %s
                    )
                """
                params.extend([indicators_tf, indicators_tf])
            else:
                raise ValueError(f"Unsupported table for multi-timeframe: {field_info['table']}")
            
            # Add the condition
            sql_operator = OPERATORS.get(operator.value)
            if not sql_operator:
                raise ValueError(f"Unsupported operator: {operator}")
            
            if operator.value == "between":
                subquery += f" AND {field_ref} BETWEEN %s AND %s"
                params.extend(value)
            elif operator.value in ["in", "not_in"]:
                placeholders = ",".join(["%s"] * len(value))
                subquery += f" AND {field_ref} {sql_operator} ({placeholders})"
                params.extend(value)
            elif operator.value in ["is_null", "is_not_null"]:
                subquery += f" AND {field_ref} {sql_operator}"
            else:
                subquery += f" AND {field_ref} {sql_operator} %s"
                params.append(value)
            
            subquery += ")"
            conditions.append(subquery)
        
        # Combine conditions based on logic
        logic_op = " AND " if multi_filter.logic.value == "AND" else " OR "
        combined_condition = logic_op.join(conditions)
        
        return f"({combined_condition})", params
    
    def build_fundamentals_condition(self, fund_filter: FundamentalsFilter) -> Tuple[str, List]:
        """Build SQL condition for fundamentals filter"""
        field = fund_filter.field
        operator = fund_filter.operator
        value = fund_filter.value
        
        # Validate field exists and is a fundamentals field
        if field not in AVAILABLE_FIELDS:
            raise ValueError(f"Unknown field: {field}")
        
        field_info = AVAILABLE_FIELDS[field]
        if field_info["table"] != "fundamentals":
            raise ValueError(f"Field {field} is not a fundamentals field")
        
        field_ref = f"f.{field}"
        params = []
        
        sql_operator = OPERATORS.get(operator.value)
        if not sql_operator:
            raise ValueError(f"Unsupported operator: {operator}")
        
        if operator.value == "between":
            if not isinstance(value, list) or len(value) != 2:
                raise ValueError("Between operator requires exactly 2 values")
            condition = f"{field_ref} BETWEEN %s AND %s"
            params.extend(value)
        elif operator.value in ["in", "not_in"]:
            if not isinstance(value, list):
                raise ValueError(f"{operator} operator requires a list of values")
            placeholders = ",".join(["%s"] * len(value))
            condition = f"{field_ref} {sql_operator} ({placeholders})"
            params.extend(value)
        elif operator.value in ["is_null", "is_not_null"]:
            condition = f"{field_ref} {sql_operator}"
        else:
            condition = f"{field_ref} {sql_operator} %s"
            params.append(value)
        
        return condition, params

    def build_simple_condition(self, filter_obj: SimpleFilter) -> Tuple[str, List]:
        """Build SQL condition from simple filter - delegated to base QueryBuilder"""
        temp_builder = QueryBuilder(self.primary_timeframe)
        return temp_builder.build_simple_condition(filter_obj)
    
    def build_expression_condition(self, expression: str) -> Tuple[str, List]:
        """Build SQL condition from expression - delegated to base QueryBuilder"""
        temp_builder = QueryBuilder(self.primary_timeframe)
        return temp_builder.build_expression_condition(expression)
    
    def build_template_condition(self, template: TemplateFilter) -> Tuple[str, List]:
        """Build SQL condition from template - delegated to base QueryBuilder"""
        temp_builder = QueryBuilder(self.primary_timeframe)
        return temp_builder.build_template_condition(template)
    
    def build_sort_clause(self, sort_configs: List[SortConfig]) -> str:
        """Build ORDER BY clause"""
        if not sort_configs:
            return ""
        
        sort_parts = []
        for sort_config in sort_configs:
            field = sort_config.field
            direction = sort_config.direction.value.upper()
            
            if field not in AVAILABLE_FIELDS:
                raise ValueError(f"Unknown sort field: {field}")
            
            field_info = AVAILABLE_FIELDS[field]
            
            # Handle fundamentals fields
            if field in FUNDAMENTALS_FIELDS:
                field_ref = f"f.{field}"
            elif field_info["table"] == "candles":
                field_ref = f"c.{field}"
            else:
                field_ref = f"i.{field}"
            
            sort_parts.append(f"{field_ref} {direction}")
        
        return f" ORDER BY {', '.join(sort_parts)}"
    
    def build_pagination_clause(self, pagination: PaginationConfig) -> str:
        """Build LIMIT and OFFSET clause"""
        if not pagination:
            return " LIMIT 100"  # Default limit
        
        clause = f" LIMIT {pagination.limit}"
        if pagination.offset > 0:
            clause += f" OFFSET {pagination.offset}"
        
        return clause

class QueryBuilder:
    """Builds optimized SQL queries for stock screening"""
    
    def __init__(self, timeframe: str):
        self.timeframe = timeframe
        self.indicators_timeframe = TIMEFRAME_INDICATORS_MAP.get(timeframe, timeframe)
        self.table_name = TIMEFRAME_TABLE_MAP.get(timeframe)
        if not self.table_name:
            raise ValueError(f"Invalid timeframe: {timeframe}")
        
        self.expression_parser = ExpressionParser()
        self.template_manager = get_template_manager()
        
    def build_base_query(self, include_latest_only: bool = True, include_fundamentals: bool = False) -> str:
        """Build the base query with proper joins"""
        # Fundamentals selection
        fundamentals_select = ""
        fundamentals_join = ""
        
        if include_fundamentals:
            fundamentals_select = """,
            f.market_cap, f.enterprise_value, f.trailing_pe, f.forward_pe, f.peg_ratio,
            f.price_to_book, f.price_to_sales, f.enterprise_to_revenue, f.enterprise_to_ebitda,
            f.roe, f.roa, f.gross_margin, f.operating_margin, f.profit_margin, f.ebitda_margin,
            f.free_cash_flow, f.operating_cash_flow, f.debt_to_equity, f.current_ratio,
            f.total_debt, f.total_cash, f.revenue_growth, f.earnings_growth,
            f.quarterly_revenue_growth, f.quarterly_earnings_growth, f.dividend_yield,
            f.dividend_rate, f.payout_ratio, f.insider_holding, f.institutional_holding,
            f.float_shares, f.shares_outstanding, f.beta, f.short_ratio,
            f.short_percent_of_float, f.previous_close, f.fifty_day_avg, f.two_hundred_day_avg,
            f.current_price, f.updated_at"""
            
            conversion_clause = get_symbol_conversion_clause()
            fundamentals_join = f"""
        LEFT JOIN fundamentals f ON {conversion_clause}"""
        
        base_query = f"""
        SELECT 
            c.symbol,
            c.datetime,
            c.open,
            c.high,
            c.low,
            c.close,
            c.volume,
            i.sma_9, i.sma_21, i.sma_50, i.sma_100, i.sma_200,
            i.ema_9, i.ema_21, i.ema_50, i.ema_100, i.ema_200,
            i.wma_9, i.wma_21, i.wma_50, i.wma_100, i.wma_200,
            i.hma_9, i.hma_21, i.hma_50, i.hma_100,
            i.rsi_7, i.rsi_14, i.rsi_21,
            i.macd_12_26_9, i.macd_signal_12_26_9, i.macd_hist_12_26_9,
            i.stochastic_k_14_3_3, i.stochastic_d_14_3_3,
            i.stochastic_k_9_3_3, i.stochastic_d_9_3_3,
            i.atr_14, i.cci_14, i.willr_14, i.roc_14, i.ao_5_34,
            i.obv, i.vwap, i.mfi_14, i.cmf_20,
            i.volume_osc_14_28, i.volume_sma_20,
            i.plus_di_14, i.minus_di_14, i.adx_14,
            i.bb_upper_20_2, i.bb_mid_20_2, i.bb_lower_20_2,
            i.keltner_upper_20_2, i.keltner_mid_20, i.keltner_lower_20_2,
            i.donchian_upper_20, i.donchian_lower_20,
            i.stddev_20, i.pivot, i.pivot_r1, i.pivot_s1, i.pivot_r2, i.pivot_s2,
            i.ichimoku_tenkan_sen, i.ichimoku_kijun_sen, 
            i.ichimoku_senkou_span_a, i.ichimoku_senkou_span_b, i.ichimoku_chikou_span,
            i.supertrend_10_3, i.supertrend_14_2,
            i.tema_20, i.tema_50, i.tema_100
            {fundamentals_select}
        FROM {self.table_name} c
        JOIN indicators i ON c.datetime = i.datetime 
            AND c.symbol = i.symbol 
            AND i.timeframe = %s
        {fundamentals_join}
        """
        
        if include_latest_only:
            base_query += f"""
            WHERE c.datetime = (
                SELECT MAX(datetime) FROM {self.table_name}
            )
            """
        
        return base_query
    
    def build_simple_condition(self, filter_obj: SimpleFilter) -> Tuple[str, List]:
        """Build SQL condition for a simple filter"""
        field = filter_obj.field
        operator = filter_obj.operator
        value = filter_obj.value
        reference = filter_obj.reference
        multiplier = filter_obj.multiplier or 1.0
        
        # Validate field exists
        if field not in AVAILABLE_FIELDS:
            raise ValueError(f"Unknown field: {field}")
        
        # Determine table alias based on field
        field_info = AVAILABLE_FIELDS[field]
        if field in FUNDAMENTALS_FIELDS:
            field_ref = f"f.{field}"
        elif field_info["table"] == "candles":
            field_ref = f"c.{field}"
        else:
            field_ref = f"i.{field}"
        
        params = []
        
        if reference:
            # Field-to-field comparison
            if reference not in AVAILABLE_FIELDS:
                raise ValueError(f"Unknown reference field: {reference}")
            
            ref_info = AVAILABLE_FIELDS[reference]
            if reference in FUNDAMENTALS_FIELDS:
                ref_field = f"f.{reference}"
            elif ref_info["table"] == "candles":
                ref_field = f"c.{reference}"
            else:
                ref_field = f"i.{reference}"
            
            if multiplier != 1.0:
                right_side = f"({ref_field} * %s)"
                params.append(multiplier)
            else:
                right_side = ref_field
            
            sql_operator = OPERATORS.get(operator.value)
            if not sql_operator:
                raise ValueError(f"Unsupported operator: {operator}")
            
            condition = f"{field_ref} {sql_operator} {right_side}"
        
        else:
            # Field-to-value comparison
            sql_operator = OPERATORS.get(operator.value)
            if not sql_operator:
                raise ValueError(f"Unsupported operator: {operator}")
            
            if operator.value == "between":
                if not isinstance(value, list) or len(value) != 2:
                    raise ValueError("Between operator requires exactly 2 values")
                condition = f"{field_ref} BETWEEN %s AND %s"
                params.extend(value)
            
            elif operator.value in ["in", "not_in"]:
                if not isinstance(value, list):
                    raise ValueError(f"{operator} operator requires a list of values")
                placeholders = ",".join(["%s"] * len(value))
                condition = f"{field_ref} {sql_operator} ({placeholders})"
                params.extend(value)
            
            elif operator.value in ["is_null", "is_not_null"]:
                condition = f"{field_ref} {sql_operator}"
            
            else:
                condition = f"{field_ref} {sql_operator} %s"
                params.append(value)
        
        return condition, params
    
    def build_expression_condition(self, expression: str) -> Tuple[str, List]:
        """Build SQL condition from expression"""
        validated_expr = self.expression_parser.validate_expression(expression)
        
        # Replace field names with proper table aliases
        def replace_field(match):
            field = match.group(1)
            if field.upper() in self.expression_parser.allowed_functions:
                return field  # Keep functions as-is
            if field in AVAILABLE_FIELDS:
                field_info = AVAILABLE_FIELDS[field]
                if field in FUNDAMENTALS_FIELDS:
                    return f"f.{field}"
                elif field_info["table"] == "candles":
                    return f"c.{field}"
                else:
                    return f"i.{field}"
            return field  # Keep unknown fields as-is (will be caught in validation)
        
        # Replace field references with proper aliases
        processed_expr = self.expression_parser.field_pattern.sub(replace_field, validated_expr)
        
        return f"({processed_expr})", []
    
    def build_template_condition(self, template: TemplateFilter) -> Tuple[str, List]:
        """Build SQL condition from template"""
        template_sql = self.template_manager.build_template_sql(
            template.name, 
            template.params
        )
        
        # Replace field names with proper table aliases (similar to expressions)
        def replace_field(match):
            field = match.group(1)
            if field in AVAILABLE_FIELDS:
                field_info = AVAILABLE_FIELDS[field]
                if field in FUNDAMENTALS_FIELDS:
                    return f"f.{field}"
                elif field_info["table"] == "candles":
                    return f"c.{field}"
                else:
                    return f"i.{field}"
            return field
        
        field_pattern = re.compile(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b')
        processed_sql = field_pattern.sub(replace_field, template_sql)
        
        return f"({processed_sql})", []
    
    def build_sort_clause(self, sort_configs: List[SortConfig]) -> str:
        """Build ORDER BY clause"""
        if not sort_configs:
            return ""
        
        sort_parts = []
        for sort_config in sort_configs:
            field = sort_config.field
            direction = sort_config.direction.value.upper()
            
            if field not in AVAILABLE_FIELDS:
                raise ValueError(f"Unknown sort field: {field}")
            
            field_info = AVAILABLE_FIELDS[field]
            if field in FUNDAMENTALS_FIELDS:
                field_ref = f"f.{field}"
            elif field_info["table"] == "candles":
                field_ref = f"c.{field}"
            else:
                field_ref = f"i.{field}"
            
            sort_parts.append(f"{field_ref} {direction}")
        
        return f" ORDER BY {', '.join(sort_parts)}"
    
    def build_pagination_clause(self, pagination: PaginationConfig) -> str:
        """Build LIMIT and OFFSET clause"""
        if not pagination:
            return " LIMIT 100"  # Default limit
        
        clause = f" LIMIT {pagination.limit}"
        if pagination.offset > 0:
            clause += f" OFFSET {pagination.offset}"
        
        return clause
    
    def build_query(
        self,
        simple_filters: Optional[List[SimpleFilter]] = None,
        expression: Optional[str] = None,
        templates: Optional[List[TemplateFilter]] = None,
        logic: str = "AND",
        sort_configs: Optional[List[SortConfig]] = None,
        pagination: Optional[PaginationConfig] = None,
        grouping: Optional[Dict[str, str]] = None,
        include_fundamentals: bool = False
    ) -> Tuple[str, List]:
        """Build complete SQL query with all filters"""
        
        # Start with base query
        base_query = self.build_base_query(include_fundamentals=include_fundamentals)
        params = [self.indicators_timeframe]  # Parameter for timeframe in base query
        
        # Collect all WHERE conditions
        where_conditions = []
        
        # Process simple filters
        if simple_filters:
            simple_conditions = []
            for simple_filter in simple_filters:
                condition, filter_params = self.build_simple_condition(simple_filter)
                simple_conditions.append(condition)
                params.extend(filter_params)
            
            if simple_conditions:
                simple_logic = grouping.get("simple_logic", "AND") if grouping else "AND"
                combined_simple = f" {simple_logic} ".join(simple_conditions)
                where_conditions.append(f"({combined_simple})")
        
        # Process expressions
        if expression:
            expr_condition, expr_params = self.build_expression_condition(expression)
            where_conditions.append(expr_condition)
            params.extend(expr_params)
        
        # Process templates
        if templates:
            template_conditions = []
            for template in templates:
                condition, template_params = self.build_template_condition(template)
                template_conditions.append(condition)
                params.extend(template_params)
            
            if template_conditions:
                template_logic = grouping.get("template_logic", "OR") if grouping else "OR"
                combined_templates = f" {template_logic} ".join(template_conditions)
                where_conditions.append(f"({combined_templates})")
        
        # Combine all WHERE conditions
        if where_conditions:
            main_logic = logic.upper()
            combined_where = f" {main_logic} ".join(where_conditions)
            
            # Add to base query
            if "WHERE" in base_query:
                base_query += f" AND ({combined_where})"
            else:
                base_query += f" WHERE ({combined_where})"
        
        # Add sorting
        if sort_configs:
            base_query += self.build_sort_clause(sort_configs)
        else:
            # Default sort by volume descending
            base_query += " ORDER BY c.volume DESC"
        
        # Add pagination
        base_query += self.build_pagination_clause(pagination)
        
        logger.info(f"Built query with {len(params)} parameters")
        logger.debug(f"Query: {base_query}")
        
        return base_query, params
    
    def estimate_query_complexity(
        self,
        simple_filters: Optional[List[SimpleFilter]] = None,
        expression: Optional[str] = None,
        templates: Optional[List[TemplateFilter]] = None
    ) -> str:
        """Estimate query complexity for performance monitoring"""
        complexity_score = 0
        
        # Simple filters are least complex
        if simple_filters:
            complexity_score += len(simple_filters) * 1
        
        # Expressions are more complex
        if expression:
            complexity_score += 3
            # Additional complexity for window functions
            if "LAG(" in expression.upper() or "LEAD(" in expression.upper():
                complexity_score += 2
        
        # Templates vary in complexity
        if templates:
            for template in templates:
                template_info = self.template_manager.get_template(template.name)
                template_sql = template_info["sql"]
                if "LAG(" in template_sql.upper() or "PARTITION BY" in template_sql.upper():
                    complexity_score += 4
                else:
                    complexity_score += 2
        
        if complexity_score <= 3:
            return "low"
        elif complexity_score <= 8:
            return "medium"
        else:
            return "high" 