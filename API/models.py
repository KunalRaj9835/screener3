"""Pydantic models for request and response validation"""

from typing import Optional, List, Dict, Any, Union, Literal
from pydantic import BaseModel, Field, validator
from enum import Enum

class OperatorEnum(str, Enum):
    """Supported filter operators"""
    GT = "gt"
    GTE = "gte"
    LT = "lt" 
    LTE = "lte"
    EQ = "eq"
    NE = "ne"
    BETWEEN = "between"
    IN = "in"
    NOT_IN = "not_in"
    IS_NULL = "is_null"
    IS_NOT_NULL = "is_not_null"

class TimeframeEnum(str, Enum):
    """Supported timeframes"""
    ONE_MIN = "1min"
    THREE_MIN = "3min"
    FIVE_MIN = "5min"
    FIFTEEN_MIN = "15min"
    THIRTY_MIN = "30min"
    ONE_HOUR = "1hr"
    TWO_HOUR = "2hr"
    FOUR_HOUR = "4hr"

class SortDirectionEnum(str, Enum):
    """Sort directions"""
    ASC = "asc"
    DESC = "desc"

class LogicEnum(str, Enum):
    """Logical operators"""
    AND = "AND"
    OR = "OR"

class OutputFormatEnum(str, Enum):
    """Output formats"""
    JSON = "json"
    CSV = "csv"

class SimpleFilter(BaseModel):
    """Simple filter model for basic filtering"""
    field: str = Field(..., description="Field name to filter on")
    operator: OperatorEnum = Field(..., description="Comparison operator")
    value: Optional[Union[float, int, str, List[Union[float, int, str]]]] = Field(
        None, description="Value to compare against"
    )
    reference: Optional[str] = Field(
        None, description="Reference field for field-to-field comparison"
    )
    multiplier: Optional[float] = Field(
        1.0, description="Multiplier for reference field"
    )
    timeframe: Optional[TimeframeEnum] = Field(
        None, description="Specific timeframe for this filter (overrides default)"
    )
    description: Optional[str] = Field(
        None, description="Human-readable description of the filter"
    )

    @validator('value')
    def validate_value_for_operator(cls, v, values):
        """Validate value based on operator"""
        operator = values.get('operator')
        if operator in ['is_null', 'is_not_null'] and v is not None:
            raise ValueError(f"Value should be None for operator {operator}")
        if operator in ['between'] and (not isinstance(v, list) or len(v) != 2):
            raise ValueError("Value should be a list with exactly 2 elements for 'between' operator")
        if operator in ['in', 'not_in'] and not isinstance(v, list):
            raise ValueError("Value should be a list for 'in' and 'not_in' operators")
        return v

class MultiTimeframeFilter(BaseModel):
    """Filter that can specify different timeframes for different conditions"""
    conditions: List[SimpleFilter] = Field(..., description="List of conditions with their timeframes")
    logic: LogicEnum = Field(LogicEnum.AND, description="Logic to combine conditions")
    description: Optional[str] = Field(None, description="Description of the multi-timeframe filter")

class FundamentalsFilter(BaseModel):
    """Filter for fundamentals data"""
    field: str = Field(..., description="Fundamental field name")
    operator: OperatorEnum = Field(..., description="Comparison operator")
    value: Optional[Union[float, int, str, List[Union[float, int, str]]]] = Field(
        None, description="Value to compare against"
    )
    description: Optional[str] = Field(None, description="Human-readable description")

class TemplateFilter(BaseModel):
    """Template filter for predefined filter patterns"""
    name: str = Field(..., description="Template name")
    params: Dict[str, Any] = Field(
        default_factory=dict, description="Template parameters"
    )
    timeframe: Optional[TimeframeEnum] = Field(
        None, description="Specific timeframe for this template (overrides default)"
    )

class SortConfig(BaseModel):
    """Sort configuration"""
    field: str = Field(..., description="Field to sort by")
    direction: SortDirectionEnum = Field(
        SortDirectionEnum.ASC, description="Sort direction"
    )
    timeframe: Optional[TimeframeEnum] = Field(
        None, description="Timeframe for the sort field (if applicable)"
    )

class OutputConfig(BaseModel):
    """Output configuration"""
    fields: Optional[List[str]] = Field(
        None, description="Specific fields to include in output"
    )
    include_fundamentals: bool = Field(
        False, description="Include fundamentals data in output"
    )
    include_all_timeframes: bool = Field(
        False, description="Include data from all requested timeframes"
    )
    format: OutputFormatEnum = Field(
        OutputFormatEnum.JSON, description="Output format"
    )
    include_metadata: bool = Field(
        True, description="Include metadata in response"
    )

class PaginationConfig(BaseModel):
    """Pagination configuration"""
    limit: int = Field(100, ge=1, le=10000, description="Number of results to return")
    offset: int = Field(0, ge=0, description="Number of results to skip")

class GroupingConfig(BaseModel):
    """Grouping configuration for different filter types"""
    simple_logic: LogicEnum = Field(LogicEnum.AND, description="Logic for simple filters")
    expression_logic: LogicEnum = Field(LogicEnum.AND, description="Logic for expressions")
    template_logic: LogicEnum = Field(LogicEnum.OR, description="Logic for templates")
    fundamentals_logic: LogicEnum = Field(LogicEnum.AND, description="Logic for fundamentals filters")
    multi_timeframe_logic: LogicEnum = Field(LogicEnum.AND, description="Logic for multi-timeframe filters")

class FiltersConfig(BaseModel):
    """Main filters configuration"""
    simple: Optional[List[SimpleFilter]] = Field(
        None, description="Simple filters"
    )
    expression: Optional[str] = Field(
        None, description="Expression-based filter"
    )
    templates: Optional[List[TemplateFilter]] = Field(
        None, description="Template filters"
    )
    fundamentals: Optional[List[FundamentalsFilter]] = Field(
        None, description="Fundamentals-based filters"
    )
    multi_timeframe: Optional[List[MultiTimeframeFilter]] = Field(
        None, description="Multi-timeframe filters"
    )

class ScreenerRequest(BaseModel):
    """Main screener request model with multi-timeframe support"""
    timeframe: Union[TimeframeEnum, List[TimeframeEnum]] = Field(
        ..., description="Primary timeframe(s) for screening"
    )
    filters: FiltersConfig = Field(..., description="Filter configuration")
    logic: LogicEnum = Field(LogicEnum.AND, description="Main logic operator")
    grouping: Optional[GroupingConfig] = Field(
        None, description="Grouping configuration for filter types"
    )
    sort: Optional[List[SortConfig]] = Field(
        None, description="Sort configuration"
    )
    output: Optional[OutputConfig] = Field(
        None, description="Output configuration"
    )
    pagination: Optional[PaginationConfig] = Field(
        None, description="Pagination configuration"
    )
    require_fundamentals: bool = Field(
        False, description="Whether to require fundamentals data for results"
    )

    @validator('filters')
    def validate_filters_not_empty(cls, v):
        """Ensure at least one filter type is provided"""
        if not any([v.simple, v.expression, v.templates, v.fundamentals, v.multi_timeframe]):
            raise ValueError("At least one filter type must be provided")
        return v

    @validator('timeframe')
    def validate_timeframe_list(cls, v):
        """Validate timeframe list doesn't exceed limits"""
        if isinstance(v, list) and len(v) > 5:
            raise ValueError("Maximum 5 timeframes allowed in a single query")
        return v

class MatchReason(BaseModel):
    """Reason why a stock matched the filters"""
    filter_type: str = Field(..., description="Type of filter that matched")
    description: str = Field(..., description="Human-readable description")
    value: Optional[float] = Field(None, description="Actual value that matched")
    timeframe: Optional[str] = Field(None, description="Timeframe for the matched value")

class FundamentalsData(BaseModel):
    """Fundamentals data structure"""
    market_cap: Optional[int] = None
    enterprise_value: Optional[int] = None
    trailing_pe: Optional[float] = None
    forward_pe: Optional[float] = None
    peg_ratio: Optional[float] = None
    price_to_book: Optional[float] = None
    price_to_sales: Optional[float] = None
    enterprise_to_revenue: Optional[float] = None
    enterprise_to_ebitda: Optional[float] = None
    roe: Optional[float] = None
    roa: Optional[float] = None
    gross_margin: Optional[float] = None
    operating_margin: Optional[float] = None
    profit_margin: Optional[float] = None
    ebitda_margin: Optional[float] = None
    free_cash_flow: Optional[int] = None
    operating_cash_flow: Optional[int] = None
    debt_to_equity: Optional[float] = None
    current_ratio: Optional[float] = None
    total_debt: Optional[int] = None
    total_cash: Optional[int] = None
    revenue_growth: Optional[float] = None
    earnings_growth: Optional[float] = None
    quarterly_revenue_growth: Optional[float] = None
    quarterly_earnings_growth: Optional[float] = None
    dividend_yield: Optional[float] = None
    dividend_rate: Optional[float] = None
    payout_ratio: Optional[float] = None
    insider_holding: Optional[float] = None
    institutional_holding: Optional[float] = None
    float_shares: Optional[int] = None
    shares_outstanding: Optional[int] = None
    beta: Optional[float] = None
    short_ratio: Optional[float] = None
    short_percent_of_float: Optional[float] = None
    previous_close: Optional[float] = None
    fifty_day_avg: Optional[float] = None
    two_hundred_day_avg: Optional[float] = None
    current_price: Optional[float] = None
    updated_at: Optional[str] = None

class TimeframeData(BaseModel):
    """Data for a specific timeframe"""
    timeframe: str = Field(..., description="Timeframe identifier")
    datetime: str = Field(..., description="Datetime of the data")
    close: Optional[float] = Field(None, description="Close price")
    volume: Optional[float] = Field(None, description="Volume")
    indicators: Dict[str, Optional[float]] = Field(
        default_factory=dict, description="Technical indicators for this timeframe"
    )

class StockResult(BaseModel):
    """Individual stock result with multi-timeframe support"""
    symbol: str = Field(..., description="Stock symbol")
    primary_timeframe: str = Field(..., description="Primary timeframe used")
    primary_datetime: str = Field(..., description="Primary datetime of the data")
    close: Optional[float] = Field(None, description="Close price (primary timeframe)")
    volume: Optional[float] = Field(None, description="Volume (primary timeframe)")
    indicators: Dict[str, Optional[float]] = Field(
        default_factory=dict, description="Technical indicators (primary timeframe)"
    )
    timeframe_data: Optional[List[TimeframeData]] = Field(
        None, description="Data from additional timeframes"
    )
    fundamentals: Optional[FundamentalsData] = Field(
        None, description="Fundamentals data"
    )
    match_reasons: Optional[List[MatchReason]] = Field(
        None, description="Reasons why this stock matched"
    )

class ScreenerMetadata(BaseModel):
    """Metadata about the screening operation"""
    total_results: int = Field(..., description="Total number of results")
    execution_time_ms: float = Field(..., description="Execution time in milliseconds")
    filters_applied: Dict[str, int] = Field(
        ..., description="Count of each filter type applied"
    )
    query_complexity: str = Field(..., description="Query complexity level")
    cache_hit: bool = Field(False, description="Whether result was from cache")

class PaginationInfo(BaseModel):
    """Pagination information"""
    current_page: int = Field(..., description="Current page number")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there are more pages")
    has_previous: bool = Field(..., description="Whether there are previous pages")

class ScreenerResponse(BaseModel):
    """Main screener response model"""
    status: Literal["success", "error"] = Field(..., description="Response status")
    metadata: Optional[ScreenerMetadata] = Field(None, description="Response metadata")
    results: List[StockResult] = Field(default_factory=list, description="Screening results")
    pagination: Optional[PaginationInfo] = Field(None, description="Pagination information")
    error: Optional[str] = Field(None, description="Error message if status is error")

class FieldInfo(BaseModel):
    """Information about an available field"""
    name: str = Field(..., description="Field name")
    type: str = Field(..., description="Field data type")
    table: str = Field(..., description="Source table")
    description: Optional[str] = Field(None, description="Field description")

class TemplateInfo(BaseModel):
    """Information about an available template"""
    name: str = Field(..., description="Template name")
    description: str = Field(..., description="Template description")
    parameters: Dict[str, Any] = Field(..., description="Template parameters")
    category: Optional[str] = Field(None, description="Template category")

class AvailableFieldsResponse(BaseModel):
    """Response for available fields endpoint"""
    status: Literal["success"] = "success"
    fields: List[FieldInfo] = Field(..., description="Available fields")
    timeframes: List[str] = Field(..., description="Available timeframes")
    operators: List[str] = Field(..., description="Available operators")

class AvailableTemplatesResponse(BaseModel):
    """Response for available templates endpoint"""
    status: Literal["success"] = "success"
    templates: List[TemplateInfo] = Field(..., description="Available templates")
    categories: List[str] = Field(..., description="Template categories")

class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: Literal["healthy", "unhealthy"] = Field(..., description="Health status")
    database: str = Field(..., description="Database connection status")
    cache: str = Field(..., description="Cache connection status")
    timestamp: str = Field(..., description="Timestamp of health check")
    version: str = Field(..., description="API version") 