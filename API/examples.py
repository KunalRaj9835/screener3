"""Enhanced API Examples - Core Functionality Showcase"""

import requests
import json
from typing import Dict, Any

# API base URL
BASE_URL = "http://localhost:8001/api/v1"

def example_1_multi_timeframe_momentum():
    """Example 1: Multi-timeframe momentum analysis (RSI + MACD)"""
    print("=== Example 1: Multi-Timeframe Momentum Strategy ===")
    
    request_data = {
        "timeframe": ["5min", "15min"],
        "filters": {
            "multi_timeframe": [
                {
                    "conditions": [
                        {
                            "field": "rsi_14",
                            "operator": "gt",
                            "value": 60,
                            "timeframe": "5min"
                        },
                        {
                            "field": "macd_12_26_9", 
                            "operator": "gt",
                            "reference": "macd_signal_12_26_9",
                            "timeframe": "15min"
                        }
                    ],
                    "logic": "AND",
                    "description": "Strong momentum on 5min + bullish MACD on 15min"
                }
            ]
        },
        "output": {
            "include_all_timeframes": True,
            "include_metadata": True
        },
        "pagination": {"limit": 5}
    }
    
    response = requests.post(f"{BASE_URL}/screen", json=request_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Found {data['metadata']['total_results']} momentum stocks")
        print(f"Execution time: {data['metadata']['execution_time_ms']:.2f}ms")
        for stock in data['results']:
            print(f"  {stock['symbol']}: Multi-timeframe momentum detected")
    print()

def example_2_fundamentals_value_screening():
    """Example 2: Value investing with fundamentals + technical confirmation"""
    print("=== Example 2: Value Investing with Technical Confirmation ===")
    
    request_data = {
        "timeframe": "15min",
        "filters": {
            "fundamentals": [
                {
                    "field": "trailing_pe",
                    "operator": "between",
                    "value": [8, 20],
                    "description": "Reasonable PE ratio"
                },
                {
                    "field": "debt_to_equity",
                    "operator": "lt",
                    "value": 0.6,
                    "description": "Low debt"
                },
                {
                    "field": "roe",
                    "operator": "gt",
                    "value": 0.12,
                    "description": "Good profitability"
                }
            ],
            "simple": [
                {
                    "field": "rsi_14",
                    "operator": "between",
                    "value": [30, 50],
                    "description": "Not overbought technically"
                }
            ]
        },
        "logic": "AND",
        "output": {
            "include_fundamentals": True,
            "include_metadata": True
        },
        "sort": [{"field": "trailing_pe", "direction": "asc"}],
        "pagination": {"limit": 5}
    }
    
    response = requests.post(f"{BASE_URL}/screen", json=request_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Found {data['metadata']['total_results']} value stocks")
        for stock in data['results']:
            print(f"  {stock['symbol']}:")
            if stock.get('fundamentals'):
                fund = stock['fundamentals']
                print(f"    PE: {fund.get('trailing_pe')}, ROE: {fund.get('roe'):.1%}, D/E: {fund.get('debt_to_equity')}")
    print()

def example_3_expression_filter():
    """Example 3: Advanced expression filtering for breakout patterns"""
    print("=== Example 3: Breakout Pattern with Expression Filter ===")
    
    request_data = {
        "timeframe": "5min",
        "filters": {
            "expression": "(close > sma_20) AND (close > sma_50) AND (volume > volume_sma_20 * 1.5) AND (rsi_14 > 50)"
        },
        "sort": [
            {"field": "volume", "direction": "desc"},
            {"field": "rsi_14", "direction": "desc"}
        ],
        "output": {
            "fields": ["symbol", "close", "volume", "rsi_14", "sma_20", "sma_50"],
            "include_metadata": True
        },
        "pagination": {"limit": 10}
    }
    
    response = requests.post(f"{BASE_URL}/screen", json=request_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Found {data['metadata']['total_results']} breakout candidates")
        print(f"Query complexity: {data['metadata']['query_complexity']}")
        for stock in data['results'][:3]:
            print(f"  {stock['symbol']}: Volume={stock.get('volume'):,.0f}, RSI={stock.get('indicators', {}).get('rsi_14', 'N/A')}")
    print()

def get_available_fields():
    """Get available fields for querying"""
    print("=== Available Fields ===")
    response = requests.get(f"{BASE_URL}/fields")
    if response.status_code == 200:
        data = response.json()
        print(f"Timeframes: {', '.join(data['timeframes'])}")
        print(f"Total fields: {len(data['fields'])}")
        print("Sample technical fields:", [f['name'] for f in data['fields'][:5] if f['table'] == 'indicators'])
        print("Sample fundamental fields:", [f['name'] for f in data['fields'][:5] if f['table'] == 'fundamentals'])
    print()

def run_all_examples():
    """Run all examples to showcase API capabilities"""
    print("🚀 Running Stock Screener API Examples\n")
    
    # Check API health first
    try:
        health = requests.get(f"{BASE_URL}/health", timeout=5)
        if health.status_code != 200:
            print("❌ API is not responding. Please start the server with: python run.py")
            return
        print("✅ API is healthy\n")
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to API. Please start the server with: python run.py")
        return
    
    # Get available fields
    get_available_fields()
    
    # Run examples
    example_1_multi_timeframe_momentum()
    example_2_fundamentals_value_screening() 
    example_3_expression_filter()
    
    print("🎉 All examples completed!")
    print("💡 Try the interactive demo: cd demo_website && streamlit run app.py")

if __name__ == "__main__":
    run_all_examples() 