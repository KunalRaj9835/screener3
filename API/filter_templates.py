"""Predefined filter templates for common stock screening patterns"""

from typing import Dict, Any, List
from models import TemplateInfo

# Template definitions with SQL and parameters
FILTER_TEMPLATES = {
    # RSI-based templates
    "oversold_rsi": {
        "description": "Stocks with RSI below oversold threshold",
        "category": "momentum",
        "sql": "rsi_{period} < {threshold}",
        "params": {
            "period": {"type": "int", "default": 14, "min": 5, "max": 50, "description": "RSI period"},
            "threshold": {"type": "float", "default": 30, "min": 10, "max": 50, "description": "Oversold threshold"}
        }
    },
    
    "overbought_rsi": {
        "description": "Stocks with RSI above overbought threshold",
        "category": "momentum",
        "sql": "rsi_{period} > {threshold}",
        "params": {
            "period": {"type": "int", "default": 14, "min": 5, "max": 50, "description": "RSI period"},
            "threshold": {"type": "float", "default": 70, "min": 50, "max": 90, "description": "Overbought threshold"}
        }
    },
    
    "rsi_neutral": {
        "description": "Stocks with RSI in neutral range",
        "category": "momentum",
        "sql": "rsi_{period} BETWEEN {lower_bound} AND {upper_bound}",
        "params": {
            "period": {"type": "int", "default": 14, "min": 5, "max": 50, "description": "RSI period"},
            "lower_bound": {"type": "float", "default": 40, "min": 20, "max": 50, "description": "Lower bound"},
            "upper_bound": {"type": "float", "default": 60, "min": 50, "max": 80, "description": "Upper bound"}
        }
    },
    
    # Moving average crossovers
    "golden_cross": {
        "description": "Short-term MA crosses above long-term MA (bullish)",
        "category": "trend",
        "sql": """
            sma_{short_period} > sma_{long_period} 
            AND LAG(sma_{short_period}) OVER (PARTITION BY symbol ORDER BY datetime) <= 
                LAG(sma_{long_period}) OVER (PARTITION BY symbol ORDER BY datetime)
        """,
        "params": {
            "short_period": {"type": "int", "default": 50, "min": 10, "max": 100, "description": "Short MA period"},
            "long_period": {"type": "int", "default": 200, "min": 50, "max": 500, "description": "Long MA period"}
        }
    },
    
    "death_cross": {
        "description": "Short-term MA crosses below long-term MA (bearish)",
        "category": "trend",
        "sql": """
            sma_{short_period} < sma_{long_period} 
            AND LAG(sma_{short_period}) OVER (PARTITION BY symbol ORDER BY datetime) >= 
                LAG(sma_{long_period}) OVER (PARTITION BY symbol ORDER BY datetime)
        """,
        "params": {
            "short_period": {"type": "int", "default": 50, "min": 10, "max": 100, "description": "Short MA period"},
            "long_period": {"type": "int", "default": 200, "min": 50, "max": 500, "description": "Long MA period"}
        }
    },
    
    "price_above_ma": {
        "description": "Price trading above moving average",
        "category": "trend",
        "sql": "close > {ma_type}_{period} * {threshold_multiplier}",
        "params": {
            "ma_type": {"type": "str", "default": "sma", "options": ["sma", "ema", "wma", "hma"], "description": "MA type"},
            "period": {"type": "int", "default": 50, "min": 5, "max": 200, "description": "MA period"},
            "threshold_multiplier": {"type": "float", "default": 1.0, "min": 0.95, "max": 1.1, "description": "Price threshold multiplier"}
        }
    },
    
    # Volume-based templates
    "volume_breakout": {
        "description": "High volume with significant price movement",
        "category": "volume",
        "sql": """
            volume > volume_sma_20 * {volume_multiplier}
            AND ABS((close - open) / open) > {price_change_threshold}
        """,
        "params": {
            "volume_multiplier": {"type": "float", "default": 2.0, "min": 1.2, "max": 5.0, "description": "Volume spike multiplier"},
            "price_change_threshold": {"type": "float", "default": 0.02, "min": 0.01, "max": 0.1, "description": "Min price change %"}
        }
    },
    
    "high_volume": {
        "description": "Stocks with volume above average",
        "category": "volume",
        "sql": "volume > volume_sma_20 * {multiplier}",
        "params": {
            "multiplier": {"type": "float", "default": 1.5, "min": 1.1, "max": 5.0, "description": "Volume multiplier"}
        }
    },
    
    "low_volume": {
        "description": "Stocks with volume below average",
        "category": "volume",
        "sql": "volume < volume_sma_20 * {multiplier}",
        "params": {
            "multiplier": {"type": "float", "default": 0.8, "min": 0.1, "max": 0.9, "description": "Volume multiplier"}
        }
    },
    
    # MACD templates
    "bullish_macd": {
        "description": "MACD line above signal line (bullish momentum)",
        "category": "momentum",
        "sql": "macd_{fast}_{slow}_{signal} > macd_signal_{fast}_{slow}_{signal}",
        "params": {
            "fast": {"type": "int", "default": 12, "min": 5, "max": 20, "description": "Fast EMA period"},
            "slow": {"type": "int", "default": 26, "min": 15, "max": 40, "description": "Slow EMA period"},
            "signal": {"type": "int", "default": 9, "min": 5, "max": 15, "description": "Signal line period"}
        }
    },
    
    "bearish_macd": {
        "description": "MACD line below signal line (bearish momentum)",
        "category": "momentum",
        "sql": "macd_{fast}_{slow}_{signal} < macd_signal_{fast}_{slow}_{signal}",
        "params": {
            "fast": {"type": "int", "default": 12, "min": 5, "max": 20, "description": "Fast EMA period"},
            "slow": {"type": "int", "default": 26, "min": 15, "max": 40, "description": "Slow EMA period"},
            "signal": {"type": "int", "default": 9, "min": 5, "max": 15, "description": "Signal line period"}
        }
    },
    
    "macd_crossover": {
        "description": "MACD just crossed above signal line",
        "category": "momentum",
        "sql": """
            macd_{fast}_{slow}_{signal} > macd_signal_{fast}_{slow}_{signal}
            AND LAG(macd_{fast}_{slow}_{signal}) OVER (PARTITION BY symbol ORDER BY datetime) <= 
                LAG(macd_signal_{fast}_{slow}_{signal}) OVER (PARTITION BY symbol ORDER BY datetime)
        """,
        "params": {
            "fast": {"type": "int", "default": 12, "min": 5, "max": 20, "description": "Fast EMA period"},
            "slow": {"type": "int", "default": 26, "min": 15, "max": 40, "description": "Slow EMA period"},
            "signal": {"type": "int", "default": 9, "min": 5, "max": 15, "description": "Signal line period"}
        }
    },
    
    # Bollinger Bands
    "bollinger_squeeze": {
        "description": "Bollinger Bands squeeze - low volatility",
        "category": "volatility",
        "sql": "(bb_upper_20_2 - bb_lower_20_2) / close < {squeeze_threshold}",
        "params": {
            "squeeze_threshold": {"type": "float", "default": 0.04, "min": 0.01, "max": 0.1, "description": "Squeeze threshold"}
        }
    },
    
    "bollinger_breakout": {
        "description": "Price breaking out of Bollinger Bands",
        "category": "volatility",
        "sql": """
            (close > bb_upper_20_2 OR close < bb_lower_20_2)
            AND volume > volume_sma_20 * {volume_threshold}
        """,
        "params": {
            "volume_threshold": {"type": "float", "default": 1.5, "min": 1.1, "max": 3.0, "description": "Volume confirmation"}
        }
    },
    
    "bb_oversold": {
        "description": "Price near lower Bollinger Band",
        "category": "mean_reversion",
        "sql": "close < bb_lower_20_2 * {threshold}",
        "params": {
            "threshold": {"type": "float", "default": 1.01, "min": 1.0, "max": 1.05, "description": "Distance threshold"}
        }
    },
    
    "bb_overbought": {
        "description": "Price near upper Bollinger Band",
        "category": "mean_reversion",
        "sql": "close > bb_upper_20_2 * {threshold}",
        "params": {
            "threshold": {"type": "float", "default": 0.99, "min": 0.95, "max": 1.0, "description": "Distance threshold"}
        }
    },
    
    # ADX and trend strength
    "strong_trend": {
        "description": "Strong trending market (high ADX)",
        "category": "trend",
        "sql": "adx_14 > {adx_threshold}",
        "params": {
            "adx_threshold": {"type": "float", "default": 25, "min": 20, "max": 50, "description": "ADX threshold"}
        }
    },
    
    "bullish_trend": {
        "description": "Strong bullish trend (+DI > -DI and high ADX)",
        "category": "trend",
        "sql": """
            plus_di_14 > minus_di_14 
            AND adx_14 > {adx_threshold}
        """,
        "params": {
            "adx_threshold": {"type": "float", "default": 25, "min": 20, "max": 50, "description": "ADX threshold"}
        }
    },
    
    "bearish_trend": {
        "description": "Strong bearish trend (-DI > +DI and high ADX)",
        "category": "trend",
        "sql": """
            minus_di_14 > plus_di_14 
            AND adx_14 > {adx_threshold}
        """,
        "params": {
            "adx_threshold": {"type": "float", "default": 25, "min": 20, "max": 50, "description": "ADX threshold"}
        }
    },
    
    # Stochastic patterns
    "stochastic_oversold": {
        "description": "Stochastic in oversold territory",
        "category": "momentum",
        "sql": """
            stochastic_k_{k_period}_3_3 < {threshold} 
            AND stochastic_d_{k_period}_3_3 < {threshold}
        """,
        "params": {
            "k_period": {"type": "int", "default": 14, "min": 5, "max": 30, "description": "Stochastic K period"},
            "threshold": {"type": "float", "default": 20, "min": 10, "max": 30, "description": "Oversold threshold"}
        }
    },
    
    "stochastic_overbought": {
        "description": "Stochastic in overbought territory",
        "category": "momentum",
        "sql": """
            stochastic_k_{k_period}_3_3 > {threshold} 
            AND stochastic_d_{k_period}_3_3 > {threshold}
        """,
        "params": {
            "k_period": {"type": "int", "default": 14, "min": 5, "max": 30, "description": "Stochastic K period"},
            "threshold": {"type": "float", "default": 80, "min": 70, "max": 90, "description": "Overbought threshold"}
        }
    },
    
    # Multi-indicator combinations
    "momentum_breakout": {
        "description": "Multiple momentum indicators aligned bullishly",
        "category": "combination",
        "sql": """
            rsi_14 > {rsi_threshold}
            AND macd_12_26_9 > macd_signal_12_26_9
            AND close > sma_21
            AND volume > volume_sma_20 * {volume_multiplier}
        """,
        "params": {
            "rsi_threshold": {"type": "float", "default": 50, "min": 40, "max": 70, "description": "RSI threshold"},
            "volume_multiplier": {"type": "float", "default": 1.2, "min": 1.0, "max": 2.0, "description": "Volume multiplier"}
        }
    },
    
    "oversold_reversal": {
        "description": "Potential oversold reversal setup",
        "category": "combination",
        "sql": """
            rsi_14 < {rsi_threshold}
            AND close < bb_lower_20_2
            AND volume > volume_sma_20 * {volume_multiplier}
        """,
        "params": {
            "rsi_threshold": {"type": "float", "default": 35, "min": 20, "max": 40, "description": "RSI oversold level"},
            "volume_multiplier": {"type": "float", "default": 1.5, "min": 1.1, "max": 3.0, "description": "Volume confirmation"}
        }
    },
    
    # Price action patterns
    "gap_up": {
        "description": "Stocks that gapped up significantly",
        "category": "price_action",
        "sql": """
            (open - LAG(close) OVER (PARTITION BY symbol ORDER BY datetime)) / 
            LAG(close) OVER (PARTITION BY symbol ORDER BY datetime) > {gap_threshold}
        """,
        "params": {
            "gap_threshold": {"type": "float", "default": 0.02, "min": 0.01, "max": 0.1, "description": "Gap threshold %"}
        }
    },
    
    "gap_down": {
        "description": "Stocks that gapped down significantly",
        "category": "price_action",
        "sql": """
            (open - LAG(close) OVER (PARTITION BY symbol ORDER BY datetime)) / 
            LAG(close) OVER (PARTITION BY symbol ORDER BY datetime) < -{gap_threshold}
        """,
        "params": {
            "gap_threshold": {"type": "float", "default": 0.02, "min": 0.01, "max": 0.1, "description": "Gap threshold %"}
        }
    },
    
    "new_highs": {
        "description": "Stocks making new highs over specified period",
        "category": "price_action",
        "sql": """
            high = (
                SELECT MAX(high) 
                FROM {table_name} c2 
                WHERE c2.symbol = {table_alias}.symbol 
                AND c2.datetime >= {table_alias}.datetime - INTERVAL '{lookback_days} days'
                AND c2.datetime <= {table_alias}.datetime
            )
        """,
        "params": {
            "lookback_days": {"type": "int", "default": 20, "min": 5, "max": 252, "description": "Lookback period in days"}
        }
    }
}

class FilterTemplateManager:
    """Manages filter templates and their validation"""
    
    def __init__(self):
        self.templates = FILTER_TEMPLATES
    
    def get_template(self, name: str) -> Dict[str, Any]:
        """Get a specific template by name"""
        if name not in self.templates:
            raise ValueError(f"Template '{name}' not found")
        return self.templates[name]
    
    def get_all_templates(self) -> List[TemplateInfo]:
        """Get all available templates as TemplateInfo objects"""
        templates = []
        for name, template in self.templates.items():
            templates.append(TemplateInfo(
                name=name,
                description=template["description"],
                parameters=template["params"],
                category=template.get("category", "general")
            ))
        return templates
    
    def get_categories(self) -> List[str]:
        """Get all available categories"""
        categories = set()
        for template in self.templates.values():
            categories.add(template.get("category", "general"))
        return sorted(list(categories))
    
    def validate_template_params(self, name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and normalize template parameters"""
        template = self.get_template(name)
        template_params = template["params"]
        validated_params = {}
        
        for param_name, param_config in template_params.items():
            param_type = param_config["type"]
            provided_value = params.get(param_name)
            
            # Use default if not provided
            if provided_value is None:
                validated_params[param_name] = param_config["default"]
                continue
            
            # Type validation and conversion
            if param_type == "int":
                try:
                    value = int(provided_value)
                    if "min" in param_config and value < param_config["min"]:
                        raise ValueError(f"Parameter '{param_name}' must be >= {param_config['min']}")
                    if "max" in param_config and value > param_config["max"]:
                        raise ValueError(f"Parameter '{param_name}' must be <= {param_config['max']}")
                    validated_params[param_name] = value
                except (ValueError, TypeError):
                    raise ValueError(f"Parameter '{param_name}' must be an integer")
            
            elif param_type == "float":
                try:
                    value = float(provided_value)
                    if "min" in param_config and value < param_config["min"]:
                        raise ValueError(f"Parameter '{param_name}' must be >= {param_config['min']}")
                    if "max" in param_config and value > param_config["max"]:
                        raise ValueError(f"Parameter '{param_name}' must be <= {param_config['max']}")
                    validated_params[param_name] = value
                except (ValueError, TypeError):
                    raise ValueError(f"Parameter '{param_name}' must be a number")
            
            elif param_type == "str":
                if "options" in param_config and provided_value not in param_config["options"]:
                    raise ValueError(f"Parameter '{param_name}' must be one of {param_config['options']}")
                validated_params[param_name] = str(provided_value)
            
            else:
                validated_params[param_name] = provided_value
        
        return validated_params
    
    def build_template_sql(self, name: str, params: Dict[str, Any]) -> str:
        """Build SQL for a template with given parameters"""
        template = self.get_template(name)
        validated_params = self.validate_template_params(name, params)
        
        # Format the SQL template
        sql = template["sql"].format(**validated_params)
        
        # Clean up any extra whitespace
        sql = " ".join(sql.split())
        
        return sql

# Global template manager instance
template_manager = FilterTemplateManager()

def get_template_manager() -> FilterTemplateManager:
    """Get the global template manager instance"""
    return template_manager 