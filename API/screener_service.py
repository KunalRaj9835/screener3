"""Enhanced Stock Screener Service with Multi-Timeframe Support"""

import time
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

from models import (
    ScreenerRequest, ScreenerResponse, ScreenerMetadata, 
    StockResult, PaginationInfo, PaginationConfig, MatchReason, FundamentalsData,
    TimeframeData, TimeframeEnum
)
from database import get_db_manager
from query_builder import QueryBuilder, MultiTimeframeQueryBuilder
from filter_templates import get_template_manager
from config import QUERY_LIMITS

logger = logging.getLogger(__name__)

class EnhancedScreenerService:
    """Enhanced service for stock screening with multi-timeframe and fundamentals support"""
    
    def __init__(self):
        self.db_manager = get_db_manager()
        self.template_manager = get_template_manager()
    
    def screen_stocks(self, request: ScreenerRequest) -> ScreenerResponse:
        """Main method to screen stocks with multi-timeframe support"""
        start_time = time.time()
        
        try:
            # Validate request
            self._validate_request(request)
            
            # Determine if this is a multi-timeframe request
            is_multi_timeframe = (
                isinstance(request.timeframe, list) or 
                self._has_multi_timeframe_filters(request.filters) or
                self._has_timeframe_specific_filters(request.filters)
            )
            
            if is_multi_timeframe:
                return self._screen_multi_timeframe(request, start_time)
            else:
                return self._screen_single_timeframe(request, start_time)
                
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            logger.error(f"Screening failed after {execution_time:.2f}ms: {str(e)}")
            
            return ScreenerResponse(
                status="error",
                error=str(e),
                results=[]
            )
    
    def _screen_single_timeframe(self, request: ScreenerRequest, start_time: float) -> ScreenerResponse:
        """Screen stocks using single timeframe (legacy behavior)"""
        
        # Use the original QueryBuilder for single timeframe
        timeframe = request.timeframe if isinstance(request.timeframe, str) else request.timeframe[0]
        query_builder = QueryBuilder(timeframe)
        
        # Extract filter components
        simple_filters = request.filters.simple
        expression = request.filters.expression
        templates = request.filters.templates
        
        # Build grouping config
        grouping = None
        if request.grouping:
            grouping = {
                "simple_logic": request.grouping.simple_logic.value,
                "expression_logic": request.grouping.expression_logic.value,
                "template_logic": request.grouping.template_logic.value
            }
        
        # Check if fundamentals are needed
        include_fundamentals = (
            request.require_fundamentals or 
            (request.output and request.output.include_fundamentals) or
            bool(request.filters.fundamentals)
        )
        
        # Build query with fundamentals support
        query_builder.include_fundamentals = include_fundamentals
        query, params = query_builder.build_query(
            simple_filters=simple_filters,
            expression=expression,
            templates=templates,
            logic=request.logic.value,
            sort_configs=request.sort,
            pagination=request.pagination,
            grouping=grouping,
            include_fundamentals=include_fundamentals
        )
        
        # Execute query
        execution_result = self.db_manager.execute_query_with_metadata(query, tuple(params))
        raw_results = execution_result["results"]
        
        # Process results
        processed_results = self._process_single_timeframe_results(
            raw_results, request, timeframe, simple_filters, expression, templates
        )
        
        return self._build_response(processed_results, request, start_time)
    
    def _screen_multi_timeframe(self, request: ScreenerRequest, start_time: float) -> ScreenerResponse:
        """Screen stocks using enhanced multi-timeframe capabilities"""
        
        # Use the new MultiTimeframeQueryBuilder
        timeframes = request.timeframe if isinstance(request.timeframe, list) else [request.timeframe]
        query_builder = MultiTimeframeQueryBuilder(timeframes)
        
        # Build enhanced query with fundamentals support
        include_fundamentals = (
            request.require_fundamentals or 
            (request.output and request.output.include_fundamentals) or
            bool(request.filters.fundamentals)
        )
        
        # Start with base query
        base_query = query_builder.build_base_query_with_fundamentals(
            include_fundamentals=include_fundamentals
        )
        
        conditions = []
        params = [query_builder.indicators_timeframe]  # For the primary timeframe parameter
        
        # Build filter conditions
        if request.filters.simple:
            for simple_filter in request.filters.simple:
                condition, filter_params = query_builder.build_simple_condition(simple_filter)
                conditions.append(condition)
                params.extend(filter_params)
        
        if request.filters.fundamentals:
            for fund_filter in request.filters.fundamentals:
                condition, filter_params = query_builder.build_fundamentals_condition(fund_filter)
                conditions.append(condition)
                params.extend(filter_params)
        
        if request.filters.multi_timeframe:
            for multi_filter in request.filters.multi_timeframe:
                condition, filter_params = query_builder.build_multi_timeframe_condition(multi_filter)
                conditions.append(condition)
                params.extend(filter_params)
        
        if request.filters.expression:
            condition, filter_params = query_builder.build_expression_condition(request.filters.expression)
            conditions.append(condition)
            params.extend(filter_params)
        
        if request.filters.templates:
            for template in request.filters.templates:
                condition, filter_params = query_builder.build_template_condition(template)
                conditions.append(condition)
                params.extend(filter_params)
        
        # Combine conditions
        if conditions:
            logic_op = " AND " if request.logic.value == "AND" else " OR "
            where_clause = " AND (" + logic_op.join(conditions) + ")"
            base_query += where_clause
        
        # Add sorting and pagination
        if request.sort:
            sort_clause = query_builder.build_sort_clause(request.sort)
            base_query += sort_clause
        
        if request.pagination:
            pagination_clause = query_builder.build_pagination_clause(request.pagination)
            base_query += pagination_clause
        
        # Execute query
        execution_result = self.db_manager.execute_query_with_metadata(base_query, tuple(params))
        raw_results = execution_result["results"]
        
        # Process multi-timeframe results
        processed_results = self._process_multi_timeframe_results(
            raw_results, request, timeframes
        )
        
        return self._build_response(processed_results, request, start_time)
    
    def _process_single_timeframe_results(
        self,
        raw_results: List[Dict],
        request: ScreenerRequest,
        timeframe: str,
        simple_filters: Optional[List] = None,
        expression: Optional[str] = None,
        templates: Optional[List] = None
    ) -> List[StockResult]:
        """Process raw database results for single timeframe"""
        processed_results = []
        
        for row in raw_results:
            # Extract basic info
            stock_result = StockResult(
                symbol=row["symbol"],
                primary_timeframe=timeframe,
                primary_datetime=row["datetime"].isoformat() if row["datetime"] else "",
                close=row.get("close"),
                volume=row.get("volume"),
                indicators={}
            )
            
            # Add indicator values
            for key, value in row.items():
                if key not in ["symbol", "datetime", "open", "high", "low", "close", "volume", "primary_timeframe"]:
                    if value is not None:
                        stock_result.indicators[key] = float(value)
            
            # Generate match reasons if requested
            if request.output and request.output.include_metadata:
                stock_result.match_reasons = self._generate_match_reasons(
                    row, simple_filters, expression, templates, timeframe
                )
            
            processed_results.append(stock_result)
        
        return processed_results
    
    def _process_multi_timeframe_results(
        self,
        raw_results: List[Dict],
        request: ScreenerRequest,
        timeframes: List[str]
    ) -> List[StockResult]:
        """Process raw database results for multi-timeframe queries"""
        processed_results = []
        
        for row in raw_results:
            # Extract basic info
            primary_timeframe = row.get("primary_timeframe", timeframes[0])
            
            stock_result = StockResult(
                symbol=row["symbol"],
                primary_timeframe=primary_timeframe,
                primary_datetime=row["datetime"].isoformat() if row["datetime"] else "",
                close=row.get("close"),
                volume=row.get("volume"),
                indicators={}
            )
            
            # Process fundamentals data if available
            if request.output and request.output.include_fundamentals:
                stock_result.fundamentals = self._extract_fundamentals_data(row)
            
            # Add indicator values for primary timeframe
            for key, value in row.items():
                if self._is_indicator_field(key) and value is not None:
                    stock_result.indicators[key] = float(value)
            
            # Add additional timeframe data if requested
            if request.output and request.output.include_all_timeframes and len(timeframes) > 1:
                stock_result.timeframe_data = self._fetch_additional_timeframe_data(
                    row["symbol"], timeframes[1:]
                )
            
            processed_results.append(stock_result)
        
        return processed_results
    
    def _extract_fundamentals_data(self, row: Dict) -> Optional[FundamentalsData]:
        """Extract fundamentals data from query result"""
        fundamentals_fields = [
            "market_cap", "enterprise_value", "trailing_pe", "forward_pe", "peg_ratio",
            "price_to_book", "price_to_sales", "enterprise_to_revenue", "enterprise_to_ebitda",
            "roe", "roa", "gross_margin", "operating_margin", "profit_margin", "ebitda_margin",
            "free_cash_flow", "operating_cash_flow", "debt_to_equity", "current_ratio",
            "total_debt", "total_cash", "revenue_growth", "earnings_growth",
            "quarterly_revenue_growth", "quarterly_earnings_growth", "dividend_yield",
            "dividend_rate", "payout_ratio", "insider_holding", "institutional_holding",
            "float_shares", "shares_outstanding", "beta", "short_ratio",
            "short_percent_of_float", "previous_close", "fifty_day_avg", "two_hundred_day_avg",
            "current_price", "updated_at"
        ]
        
        fundamentals_data = {}
        has_data = False
        
        for field in fundamentals_fields:
            if field in row and row[field] is not None:
                fundamentals_data[field] = row[field]
                has_data = True
        
        if has_data:
            if "updated_at" in fundamentals_data and fundamentals_data["updated_at"]:
                fundamentals_data["updated_at"] = fundamentals_data["updated_at"].isoformat()
            return FundamentalsData(**fundamentals_data)
        
        return None
    
    def _fetch_additional_timeframe_data(self, symbol: str, timeframes: List[str]) -> List[TimeframeData]:
        """Fetch data from additional timeframes for a specific symbol"""
        additional_data = []
        
        for timeframe in timeframes:
            try:
                # Use single timeframe query builder to get data
                query_builder = QueryBuilder(timeframe)
                base_query = query_builder.build_base_query()
                
                # Add symbol filter
                query = f"{base_query} AND c.symbol = %s LIMIT 1"
                
                result = self.db_manager.execute_query(query, (query_builder.indicators_timeframe, symbol))
                
                if result:
                    row = result[0]
                    timeframe_data = TimeframeData(
                        timeframe=timeframe,
                        datetime=row["datetime"].isoformat() if row["datetime"] else "",
                        close=row.get("close"),
                        volume=row.get("volume"),
                        indicators={}
                    )
                    
                    # Add indicators
                    for key, value in row.items():
                        if self._is_indicator_field(key) and value is not None:
                            timeframe_data.indicators[key] = float(value)
                    
                    additional_data.append(timeframe_data)
                    
            except Exception as e:
                logger.warning(f"Failed to fetch {timeframe} data for {symbol}: {e}")
                continue
        
        return additional_data
    
    def _is_indicator_field(self, field_name: str) -> bool:
        """Check if a field name represents an indicator"""
        excluded_fields = {
            "symbol", "datetime", "open", "high", "low", "close", "volume", 
            "primary_timeframe", "updated_at"
        }
        return field_name not in excluded_fields and not field_name.startswith("market_cap")
    
    def _has_multi_timeframe_filters(self, filters) -> bool:
        """Check if request contains multi-timeframe filters"""
        return bool(filters.multi_timeframe)
    
    def _has_timeframe_specific_filters(self, filters) -> bool:
        """Check if any filters specify different timeframes"""
        if filters.simple:
            for f in filters.simple:
                if f.timeframe:
                    return True
        if filters.templates:
            for t in filters.templates:
                if t.timeframe:
                    return True
        return False
    
    def _validate_request(self, request: ScreenerRequest):
        """Validate the screening request"""
        # Check if any filters are provided
        filters = request.filters
        if not any([filters.simple, filters.expression, filters.templates, filters.fundamentals, filters.multi_timeframe]):
            raise ValueError("At least one filter must be provided")
        
        # Validate pagination limits
        if request.pagination and request.pagination.limit > QUERY_LIMITS["max_results"]:
            raise ValueError(f"Limit cannot exceed {QUERY_LIMITS['max_results']}")
        
        # Validate template names
        if filters.templates:
            for template in filters.templates:
                try:
                    self.template_manager.get_template(template.name)
                except ValueError as e:
                    raise ValueError(f"Invalid template: {str(e)}")
        
        # Validate multi-timeframe combinations
        if isinstance(request.timeframe, list) and len(request.timeframe) > QUERY_LIMITS["max_timeframe_combinations"]:
            raise ValueError(f"Maximum {QUERY_LIMITS['max_timeframe_combinations']} timeframes allowed")
        
        # Validate fundamentals fields
        if filters.fundamentals:
            from config import AVAILABLE_FIELDS
            for fund_filter in filters.fundamentals:
                field_info = AVAILABLE_FIELDS.get(fund_filter.field)
                if not field_info or field_info["table"] != "fundamentals":
                    raise ValueError(f"Invalid fundamentals field: {fund_filter.field}")
    
    def _process_results(
        self,
        raw_results: List[Dict],
        request: ScreenerRequest,
        simple_filters: Optional[List] = None,
        expression: Optional[str] = None,
        templates: Optional[List] = None
    ) -> List[StockResult]:
        """Process raw database results into StockResult objects"""
        processed_results = []
        
        for row in raw_results:
            # Extract basic info
            stock_result = StockResult(
                symbol=row["symbol"],
                datetime=row["datetime"].isoformat() if row["datetime"] else "",
                close=row.get("close"),
                volume=row.get("volume"),
                indicators={}
            )
            
            # Add indicator values
            for key, value in row.items():
                if key not in ["symbol", "datetime", "open", "high", "low", "close", "volume"]:
                    if value is not None:
                        stock_result.indicators[key] = float(value)
            
            # Generate match reasons if requested
            if request.output and request.output.include_metadata:
                stock_result.match_reasons = self._generate_match_reasons(
                    row, simple_filters, expression, templates
                )
            
            # Filter output fields if specified
            if request.output and request.output.fields:
                self._filter_output_fields(stock_result, request.output.fields)
            
            processed_results.append(stock_result)
        
        return processed_results
    
    def _generate_match_reasons(
        self,
        row: Dict,
        simple_filters: Optional[List] = None,
        expression: Optional[str] = None,
        templates: Optional[List] = None,
        timeframe: str = None
    ) -> List[MatchReason]:
        """Generate reasons why a stock matched the filters"""
        reasons = []
        
        # Simple filter reasons
        if simple_filters:
            for filter_obj in simple_filters:
                field_value = row.get(filter_obj.field)
                if field_value is not None:
                    reason = MatchReason(
                        filter_type="simple",
                        description=f"{filter_obj.field} {filter_obj.operator.value} {filter_obj.value}",
                        value=float(field_value),
                        timeframe=timeframe
                    )
                    reasons.append(reason)
        
        # Expression reasons
        if expression:
            reason = MatchReason(
                filter_type="expression",
                description=f"Expression: {expression}",
                timeframe=timeframe
            )
            reasons.append(reason)
        
        # Template reasons
        if templates:
            for template in templates:
                reason = MatchReason(
                    filter_type="template",
                    description=f"Template: {template.name}",
                    timeframe=timeframe
                )
                reasons.append(reason)
        
        return reasons
    
    def _filter_output_fields(self, stock_result: StockResult, allowed_fields: List[str]):
        """Filter stock result to only include specified fields"""
        # Always keep symbol and datetime
        base_fields = {"symbol", "datetime"}
        allowed_set = set(allowed_fields) | base_fields
        
        # Filter indicators
        filtered_indicators = {}
        for key, value in stock_result.indicators.items():
            if key in allowed_set:
                filtered_indicators[key] = value
        
        stock_result.indicators = filtered_indicators
        
        # Filter basic fields
        if "close" not in allowed_set:
            stock_result.close = None
        if "volume" not in allowed_set:
            stock_result.volume = None
    
    def _calculate_pagination(
        self,
        total_results: int,
        pagination_config: Optional[PaginationConfig]
    ) -> Optional[PaginationInfo]:
        """Calculate pagination information"""
        if not pagination_config:
            return None
        
        limit = pagination_config.limit
        offset = pagination_config.offset
        
        current_page = (offset // limit) + 1
        total_pages = (total_results + limit - 1) // limit
        has_next = offset + limit < total_results
        has_previous = offset > 0
        
        return PaginationInfo(
            current_page=current_page,
            total_pages=total_pages,
            has_next=has_next,
            has_previous=has_previous
        )
    
    def get_available_fields(self) -> Dict[str, Any]:
        """Get available fields for filtering"""
        from config import AVAILABLE_FIELDS, AVAILABLE_TIMEFRAMES, OPERATORS
        
        # Create flat list of FieldInfo objects
        fields_list = []
        
        for field_name, field_info in AVAILABLE_FIELDS.items():
            fields_list.append({
                "name": field_name,
                "type": field_info["type"],
                "table": field_info["table"],
                "description": field_info.get("description", f"{field_name.replace('_', ' ').title()}")
            })
        
        return {
            "fields": fields_list,
            "timeframes": AVAILABLE_TIMEFRAMES,
            "operators": list(OPERATORS.keys())
        }
    
    def get_available_templates(self) -> Dict[str, Any]:
        """Get available filter templates"""
        templates = self.template_manager.get_all_templates()
        
        categories = set()
        template_list = []
        
        for name, template_info in templates.items():
            category = template_info.get("category", "general")
            categories.add(category)
            
            template_list.append({
                "name": name,
                "description": template_info.get("description", ""),
                "parameters": template_info.get("parameters", {}),
                "category": category
            })
        
        return {
            "templates": template_list,
            "categories": sorted(list(categories))
        }
    
    def get_data_statistics(self, timeframe: str) -> Dict[str, Any]:
        """Get data statistics for a specific timeframe"""
        try:
            from config import TIMEFRAME_TABLE_MAP
            table_name = TIMEFRAME_TABLE_MAP.get(timeframe)
            if not table_name:
                raise ValueError(f"Invalid timeframe: {timeframe}")
            
            # Get basic statistics
            stats_query = f"""
            SELECT 
                COUNT(DISTINCT symbol) as symbol_count,
                COUNT(*) as total_records,
                MIN(datetime) as earliest_date,
                MAX(datetime) as latest_date
            FROM {table_name}
            """
            
            result = self.db_manager.execute_query(stats_query)
            if result:
                stats = result[0]
                return {
                    "timeframe": timeframe,
                    "symbol_count": stats["symbol_count"],
                    "total_records": stats["total_records"],
                    "earliest_date": stats["earliest_date"].isoformat() if stats["earliest_date"] else None,
                    "latest_date": stats["latest_date"].isoformat() if stats["latest_date"] else None
                }
            
            return {"error": "No data found"}
            
        except Exception as e:
            logger.error(f"Error getting statistics for {timeframe}: {e}")
            return {"error": str(e)}
    
    def health_check(self) -> Dict[str, str]:
        """Perform health check"""
        try:
            # Test database connection
            self.db_manager.execute_query("SELECT 1")
            db_status = "healthy"
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            db_status = "unhealthy"
        
        return {
            "status": "healthy" if db_status == "healthy" else "unhealthy",
            "database": db_status,
            "cache": "not_implemented",  # TODO: Implement cache health check
            "timestamp": datetime.now().isoformat(),
            "version": "2.0.0-enhanced"
        }
    
    def _build_response(self, processed_results: List[StockResult], request: ScreenerRequest, start_time: float) -> ScreenerResponse:
        """Build the final response with metadata"""
        execution_time = (time.time() - start_time) * 1000
        
        # Calculate metadata
        total_results = len(processed_results)
        filters_applied = self._count_applied_filters(request.filters)
        complexity = self._estimate_complexity(request)
        
        # Build pagination info
        pagination_info = None
        if request.pagination:
            pagination_info = self._calculate_pagination(total_results, request.pagination)
        
        # Create metadata
        metadata = ScreenerMetadata(
            total_results=total_results,
            execution_time_ms=execution_time,
            filters_applied=filters_applied,
            query_complexity=complexity,
            cache_hit=False
        )
        
        return ScreenerResponse(
            status="success",
            metadata=metadata,
            results=processed_results,
            pagination=pagination_info
        )
    
    def _count_applied_filters(self, filters) -> Dict[str, int]:
        """Count the number of each filter type applied"""
        return {
            "simple": len(filters.simple) if filters.simple else 0,
            "expression": 1 if filters.expression else 0,
            "templates": len(filters.templates) if filters.templates else 0,
            "fundamentals": len(filters.fundamentals) if filters.fundamentals else 0,
            "multi_timeframe": len(filters.multi_timeframe) if filters.multi_timeframe else 0
        }
    
    def _estimate_complexity(self, request: ScreenerRequest) -> str:
        """Estimate query complexity"""
        complexity_score = 0
        
        if request.filters.simple:
            complexity_score += len(request.filters.simple)
        if request.filters.expression:
            complexity_score += 3
        if request.filters.templates:
            complexity_score += len(request.filters.templates) * 2
        if request.filters.fundamentals:
            complexity_score += len(request.filters.fundamentals)
        if request.filters.multi_timeframe:
            complexity_score += len(request.filters.multi_timeframe) * 4
        
        if complexity_score <= 3:
            return "low"
        elif complexity_score <= 8:
            return "medium"
        else:
            return "high"

# Global screener service instance
screener_service = EnhancedScreenerService()

def get_screener_service() -> EnhancedScreenerService:
    """Get the global screener service instance"""
    return screener_service 