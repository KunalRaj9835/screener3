"""Configuration settings for the Stock Screener API"""

import os
from typing import List

# Database Configuration
DATABASE_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "database": "screener_db",
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "password")
}

print("✅ Using DB:", DATABASE_CONFIG["database"])

# API Configuration
API_CONFIG = {
    "title": "Stock Screener API",
    "description": "High-performance stock screening and filtering API",
    "version": "1.0.0",
    "host": "0.0.0.0",
    "port": 8001,
}

# Redis Configuration (for caching)
REDIS_CONFIG = {
    "host": os.getenv("REDIS_HOST", "localhost"),
    "port": int(os.getenv("REDIS_PORT", "6379")),
    "db": int(os.getenv("REDIS_DB", "0")),
    "decode_responses": True
}

# Available timeframes
AVAILABLE_TIMEFRAMES = [
    "1min", "3min", "5min", "15min", "30min", "1hr", "2hr", "4hr"
]

# Timeframe to table mapping
TIMEFRAME_TABLE_MAP = {
    "1min": "one_min_candle_data",
    "3min": "candles_3min",
    "5min": "candles_5min", 
    "15min": "candles_15min",
    "30min": "candles_30min",
    "1hr": "candles_1hr",
    "2hr": "candles_2hr",
    "4hr": "candles_4hr"
}

# Timeframe to indicators timeframe mapping
TIMEFRAME_INDICATORS_MAP = {
    "1min": "1min",
    "3min": "3min",  # if exists in DB
    "5min": "5min", 
    "15min": "15min",
    "30min": "30min",
    "1hr": "1h",
    "2hr": "2h",
    "4hr": "4h"
}

# Cache settings
CACHE_SETTINGS = {
    "default_ttl": 300,  # 5 minutes
    "query_cache_ttl": 60,  # 1 minute for query results
    "template_cache_ttl": 3600,  # 1 hour for templates
    "max_cache_size": 1000
}

# Query limits
QUERY_LIMITS = {
    "max_results": 10000,
    "default_limit": 100,
    "max_timeframe_combinations": 5
}

# Supported operators for simple filters
OPERATORS = {
    "gt": ">",
    "gte": ">=", 
    "lt": "<",
    "lte": "<=",
    "eq": "=",
    "ne": "!=",
    "between": "BETWEEN",
    "in": "IN",
    "not_in": "NOT IN",
    "is_null": "IS NULL",
    "is_not_null": "IS NOT NULL"
}

# Available fields for filtering (based on database schema)
AVAILABLE_FIELDS = {
    # OHLCV data
    "open": {"type": "float", "table": "candles"},
    "high": {"type": "float", "table": "candles"},
    "low": {"type": "float", "table": "candles"},
    "close": {"type": "float", "table": "candles"},
    "volume": {"type": "float", "table": "candles"},
    
    # Moving Averages
    "sma_9": {"type": "float", "table": "indicators"},
    "sma_21": {"type": "float", "table": "indicators"},
    "sma_50": {"type": "float", "table": "indicators"},
    "sma_100": {"type": "float", "table": "indicators"},
    "sma_200": {"type": "float", "table": "indicators"},
    "ema_9": {"type": "float", "table": "indicators"},
    "ema_21": {"type": "float", "table": "indicators"},
    "ema_50": {"type": "float", "table": "indicators"},
    "ema_100": {"type": "float", "table": "indicators"},
    "ema_200": {"type": "float", "table": "indicators"},
    "wma_9": {"type": "float", "table": "indicators"},
    "wma_21": {"type": "float", "table": "indicators"},
    "wma_50": {"type": "float", "table": "indicators"},
    "wma_100": {"type": "float", "table": "indicators"},
    "wma_200": {"type": "float", "table": "indicators"},
    "hma_9": {"type": "float", "table": "indicators"},
    "hma_21": {"type": "float", "table": "indicators"},
    "hma_50": {"type": "float", "table": "indicators"},
    "hma_100": {"type": "float", "table": "indicators"},
    
    # Momentum Indicators
    "rsi_7": {"type": "float", "table": "indicators"},
    "rsi_14": {"type": "float", "table": "indicators"},
    "rsi_21": {"type": "float", "table": "indicators"},
    "macd_12_26_9": {"type": "float", "table": "indicators"},
    "macd_signal_12_26_9": {"type": "float", "table": "indicators"},
    "macd_hist_12_26_9": {"type": "float", "table": "indicators"},
    "stochastic_k_14_3_3": {"type": "float", "table": "indicators"},
    "stochastic_d_14_3_3": {"type": "float", "table": "indicators"},
    "stochastic_k_9_3_3": {"type": "float", "table": "indicators"},
    "stochastic_d_9_3_3": {"type": "float", "table": "indicators"},
    "atr_14": {"type": "float", "table": "indicators"},
    "cci_14": {"type": "float", "table": "indicators"},
    "willr_14": {"type": "float", "table": "indicators"},
    "roc_14": {"type": "float", "table": "indicators"},
    "ao_5_34": {"type": "float", "table": "indicators"},
    
    # Volume Indicators
    "obv": {"type": "float", "table": "indicators"},
    "vwap": {"type": "float", "table": "indicators"},
    "mfi_14": {"type": "float", "table": "indicators"},
    "cmf_20": {"type": "float", "table": "indicators"},
    "volume_osc_14_28": {"type": "float", "table": "indicators"},
    "volume_sma_20": {"type": "float", "table": "indicators"},
    
    # Trend Indicators
    "plus_di_14": {"type": "float", "table": "indicators"},
    "minus_di_14": {"type": "float", "table": "indicators"},
    "adx_14": {"type": "float", "table": "indicators"},
    "supertrend_10_3": {"type": "float", "table": "indicators"},
    "supertrend_14_2": {"type": "float", "table": "indicators"},
    
    # Bands and Channels
    "bb_upper_20_2": {"type": "float", "table": "indicators"},
    "bb_mid_20_2": {"type": "float", "table": "indicators"},
    "bb_lower_20_2": {"type": "float", "table": "indicators"},
    "keltner_upper_20_2": {"type": "float", "table": "indicators"},
    "keltner_mid_20": {"type": "float", "table": "indicators"},
    "keltner_lower_20_2": {"type": "float", "table": "indicators"},
    "donchian_upper_20": {"type": "float", "table": "indicators"},
    "donchian_lower_20": {"type": "float", "table": "indicators"},
    
    # Ichimoku
    "ichimoku_tenkan_sen": {"type": "float", "table": "indicators"},
    "ichimoku_kijun_sen": {"type": "float", "table": "indicators"},
    "ichimoku_senkou_span_a": {"type": "float", "table": "indicators"},
    "ichimoku_senkou_span_b": {"type": "float", "table": "indicators"},
    "ichimoku_chikou_span": {"type": "float", "table": "indicators"},
    
    # Pivot Points
    "pivot": {"type": "float", "table": "indicators"},
    "pivot_r1": {"type": "float", "table": "indicators"},
    "pivot_s1": {"type": "float", "table": "indicators"},
    "pivot_r2": {"type": "float", "table": "indicators"},
    "pivot_s2": {"type": "float", "table": "indicators"},
    
    # Other
    "stddev_20": {"type": "float", "table": "indicators"},
    "tema_20": {"type": "float", "table": "indicators"},
    "tema_50": {"type": "float", "table": "indicators"},
    "tema_100": {"type": "float", "table": "indicators"},
    
    # Fundamentals
    "market_cap": {"type": "int", "table": "fundamentals"},
    "enterprise_value": {"type": "int", "table": "fundamentals"},
    "trailing_pe": {"type": "float", "table": "fundamentals"},
    "forward_pe": {"type": "float", "table": "fundamentals"},
    "peg_ratio": {"type": "float", "table": "fundamentals"},
    "price_to_book": {"type": "float", "table": "fundamentals"},
    "price_to_sales": {"type": "float", "table": "fundamentals"},
    "enterprise_to_revenue": {"type": "float", "table": "fundamentals"},
    "enterprise_to_ebitda": {"type": "float", "table": "fundamentals"},
    "roe": {"type": "float", "table": "fundamentals"},
    "roa": {"type": "float", "table": "fundamentals"},
    "gross_margin": {"type": "float", "table": "fundamentals"},
    "operating_margin": {"type": "float", "table": "fundamentals"},
    "profit_margin": {"type": "float", "table": "fundamentals"},
    "ebitda_margin": {"type": "float", "table": "fundamentals"},
    "free_cash_flow": {"type": "int", "table": "fundamentals"},
    "operating_cash_flow": {"type": "int", "table": "fundamentals"},
    "debt_to_equity": {"type": "float", "table": "fundamentals"},
    "current_ratio": {"type": "float", "table": "fundamentals"},
    "total_debt": {"type": "int", "table": "fundamentals"},
    "total_cash": {"type": "int", "table": "fundamentals"},
    "revenue_growth": {"type": "float", "table": "fundamentals"},
    "earnings_growth": {"type": "float", "table": "fundamentals"},
    "quarterly_revenue_growth": {"type": "float", "table": "fundamentals"},
    "quarterly_earnings_growth": {"type": "float", "table": "fundamentals"},
    "dividend_yield": {"type": "float", "table": "fundamentals"},
    "dividend_rate": {"type": "float", "table": "fundamentals"},
    "payout_ratio": {"type": "float", "table": "fundamentals"},
    "insider_holding": {"type": "float", "table": "fundamentals"},
    "institutional_holding": {"type": "float", "table": "fundamentals"},
    "float_shares": {"type": "int", "table": "fundamentals"},
    "shares_outstanding": {"type": "int", "table": "fundamentals"},
    "beta": {"type": "float", "table": "fundamentals"},
    "short_ratio": {"type": "float", "table": "fundamentals"},
    "short_percent_of_float": {"type": "float", "table": "fundamentals"},
    "previous_close": {"type": "float", "table": "fundamentals"},
    "fifty_day_avg": {"type": "float", "table": "fundamentals"},
    "two_hundred_day_avg": {"type": "float", "table": "fundamentals"},
    "current_price": {"type": "float", "table": "fundamentals"}
}

# List of fundamentals fields for easy reference
FUNDAMENTALS_FIELDS = [
    "market_cap", "enterprise_value", "trailing_pe", "forward_pe", "peg_ratio",
    "price_to_book", "price_to_sales", "enterprise_to_revenue", "enterprise_to_ebitda",
    "roe", "roa", "gross_margin", "operating_margin", "profit_margin", "ebitda_margin",
    "free_cash_flow", "operating_cash_flow", "debt_to_equity", "current_ratio",
    "total_debt", "total_cash", "revenue_growth", "earnings_growth",
    "quarterly_revenue_growth", "quarterly_earnings_growth", "dividend_yield",
    "dividend_rate", "payout_ratio", "insider_holding", "institutional_holding",
    "float_shares", "shares_outstanding", "beta", "short_ratio",
    "short_percent_of_float", "previous_close", "fifty_day_avg",
    "two_hundred_day_avg", "current_price"
] 