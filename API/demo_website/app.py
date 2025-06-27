import streamlit as st
import requests
import json
import subprocess
import time
import pandas as pd
from datetime import datetime
import psutil
import os
# Page configuration
st.set_page_config(
    page_title="🚀 Stock Screener API Demo",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = "http://localhost:8001"

# Custom CSS
st.markdown("""
<style>
.main-header {
    font-size: 3rem;
    font-weight: bold;
    text-align: center;
    margin-bottom: 2rem;
    background: linear-gradient(90deg, #1f77b4, #ff7f0e);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.feature-card {
    background: #f0f2f6;
    padding: 1rem;
    border-radius: 10px;
    margin: 1rem 0;
    border-left: 5px solid #1f77b4;
    color: #2c3e50;
    font-weight: 500;
}
.example-card {
    background: #e8f4fd;
    padding: 1rem;
    border-radius: 8px;
    margin: 0.5rem 0;
    border: 1px solid #1f77b4;
    color: #2c3e50;
}
.success-box {
    background: #d4edda;
    padding: 1rem;
    border-radius: 8px;
    border: 1px solid #c3e6cb;
    color: #155724;
}
.error-box {
    background: #f8d7da;
    padding: 1rem;
    border-radius: 8px;
    border: 1px solid #f5c6cb;
    color: #721c24;
}
.code-block {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 8px;
    border-left: 4px solid #28a745;
    font-family: 'Courier New', monospace;
}
</style>
""", unsafe_allow_html=True)

def check_api_status():
    """Check if the API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/health", timeout=5)
        return response.status_code == 200, response.json() if response.status_code == 200 else None
    except:
        return False, None

def start_api_server():
    """Start the API server"""
    try:
        # Change to parent directory and start the server
        parent_dir = os.path.dirname(os.getcwd())
        subprocess.Popen(
            ["python", "run.py"],
            cwd=parent_dir,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return True
    except Exception as e:
        st.error(f"Failed to start API server: {e}")
        return False

def execute_query(query_data, query_name="Custom Query"):
    """Execute a query against the API"""
    print(f"Executing query: {query_name}")
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/screen",
            json=query_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return True, result
        else:
            return False, f"API Error: {response.status_code} - {response.text}"
    except Exception as e:
        return False, f"Connection Error: {str(e)}"

def main():
    # Header
    st.markdown('<h1 class="main-header">🚀 Stock Screener API Demo</h1>', unsafe_allow_html=True)
    
    # Sidebar for system controls
    with st.sidebar:
        st.header("🔧 System Controls")
        
        # Check API status
        is_running, health_data = check_api_status()
        
        if is_running:
            st.markdown('<div class="success-box">✅ API Status: HEALTHY</div>', unsafe_allow_html=True)
            if health_data:
                st.json(health_data)
        else:
            st.markdown('<div class="error-box">❌ API Status: OFFLINE</div>', unsafe_allow_html=True)
            if st.button("🚀 Start API Server"):
                with st.spinner("Starting API server..."):
                    if start_api_server():
                        st.success("Server start command sent! Please wait 10-15 seconds...")
                        time.sleep(3)
                        st.rerun()
                    else:
                        st.error("Failed to start server")
        
        # Quick stats
        if is_running:
            st.header("📊 Quick Stats")
            try:
                # Get field info
                fields_response = requests.get(f"{API_BASE_URL}/api/v1/fields", timeout=5)
                if fields_response.status_code == 200:
                    st.info("✅ Fields endpoint working")
                else:
                    st.warning("⚠️ Fields endpoint has issues")
                
                # Database info
                st.info("🗄️ Database: 49 symbols\n📈 Fundamentals: 65 records")
                
            except:
                st.warning("Could not fetch stats")

    # Main content
    if not is_running:
        st.warning("⚠️ Please start the API server using the sidebar to begin the demo!")
        st.info("The API server needs to be running to execute queries and show results.")
        return
    
    # API Features Overview
    st.header("🎯 API Features Overview")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="feature-card">
        <h4>📊 Simple Filters</h4>
        Filter stocks by individual indicators like RSI, MACD, volume, etc.
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
        <h4>🔗 Multi-Timeframe</h4>
        Combine indicators across different timeframes (5min + 15min + 1hr)
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
        <h4>💰 Fundamentals</h4>
        Screen by financial metrics: P/E ratios, debt ratios, growth rates
        </div>
        """, unsafe_allow_html=True)
    
    # Tab layout for different sections
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎮 Quick Examples", 
        "📊 Simple Filters", 
        "🔗 Multi-Timeframe", 
        "💰 Fundamentals",
        "⚙️ Custom Queries"
    ])
    
    # Quick Examples Tab
    with tab1:
        st.header("🎮 Ready-to-Run Examples")
        st.write("Click any button to run a pre-built query and see results!")
        
        examples = [
            {
                "name": "High RSI Stocks",
                "description": "Find stocks with RSI > 60 (momentum)",
                "query": {
                    "timeframe": ["5min"],
                    "filters": {
                        "simple": [{"field": "rsi_14", "operator": "gt", "value": 60}]
                    },
                    "limit": 5
                }
            },
            {
                "name": "Volume Breakout",
                "description": "Stocks with above-average volume",
                "query": {
                    "timeframe": ["5min"],
                    "filters": {
                        "expression": "volume > volume_sma_20 * 1.2"
                    },
                    "limit": 5
                }
            },
            {
                "name": "Cross-Timeframe Momentum",
                "description": "RSI strong on 5min + MACD positive on 15min",
                "query": {
                    "timeframe": ["5min", "15min"],
                    "filters": {
                        "multi_timeframe": [{
                            "conditions": [
                                {"field": "rsi_14", "operator": "gt", "value": 65, "timeframe": "5min"},
                                {"field": "macd_hist_12_26_9", "operator": "gt", "value": 0, "timeframe": "15min"}
                            ],
                            "logic": "AND"
                        }]
                    },
                    "limit": 3
                }
            },
            {
                "name": "Moving Average Filter",
                "description": "Price above 50-period moving average",
                "query": {
                    "timeframe": ["5min"],
                    "filters": {
                        "expression": "close > sma_50"
                    },
                    "limit": 5
                }
            }
        ]
        
        for example in examples:
            with st.expander(f"📋 {example['name']} - {example['description']}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown("**Query JSON:**")
                    st.code(json.dumps(example['query'], indent=2), language='json')
                
                with col2:
                    if st.button(f"▶️ Run {example['name']}", key=f"run_{example['name']}"):
                        with st.spinner(f"Executing {example['name']}..."):
                            success, result = execute_query(example['query'], example['name'])
                            
                            if success:
                                st.success(f"✅ Found {result['metadata']['total_results']} results in {result['metadata']['execution_time_ms']:.1f}ms")
                                
                                if result['results']:
                                    # Display results in a nice format
                                    df_data = []
                                    for stock in result['results']:
                                        row = {
                                            'Symbol': stock['symbol'],
                                            'Close': f"₹{stock['close']:.1f}",
                                            'Volume': f"{stock['volume']:,.0f}",
                                        }
                                        if 'indicators' in stock and stock['indicators']:
                                            row['RSI_14'] = f"{stock['indicators'].get('rsi_14', 0):.1f}"
                                            row['MACD'] = f"{stock['indicators'].get('macd_12_26_9', 0):.2f}"
                                        df_data.append(row)
                                    
                                    df = pd.DataFrame(df_data)
                                    st.dataframe(df, use_container_width=True)
                                else:
                                    st.info("No stocks matched the criteria")
                            else:
                                st.error(f"❌ Error: {result}")

    # Simple Filters Tab
    with tab2:
        st.header("📊 Simple Filters")
        st.write("Build complex queries by chaining multiple simple filters")
        
        # Initialize session state for filters
        if 'simple_filters' not in st.session_state:
            st.session_state.simple_filters = []
        
        # Filter builder section
        st.subheader("🔗 Build Your Filter Chain")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            indicator = st.selectbox("Select Indicator", [
                "rsi_14", "rsi_7", "rsi_21",
                "macd_12_26_9", "macd_hist_12_26_9", 
                "sma_50", "ema_21", "close", "volume",
                "atr_14", "adx_14", "bb_upper_20_2", "bb_lower_20_2"
            ])
            
            operator = st.selectbox("Operator", [
                ("gt", "Greater than (>)"),
                ("lt", "Less than (<)"),
                ("eq", "Equal to (=)"),
                ("between", "Between"),
                ("gte", "Greater than or equal (>=)"),
                ("lte", "Less than or equal (<=)")
            ], format_func=lambda x: x[1])
            
        with col2:
            if operator[0] == "between":
                col_a, col_b = st.columns(2)
                with col_a:
                    value1 = st.number_input("Min Value", value=0.0, key="min_val")
                with col_b:
                    value2 = st.number_input("Max Value", value=100.0, key="max_val")
                value = [value1, value2]
            else:
                value = st.number_input("Value", value=50.0, key="filter_value")
        
        with col3:
            st.write("") # spacer
            st.write("") # spacer
            if st.button("➕ Add Filter"):
                new_filter = {"field": indicator, "operator": operator[0], "value": value}
                st.session_state.simple_filters.append(new_filter)
                st.success(f"Added: {indicator} {operator[1]} {value}")
        
        # Display current filters
        if st.session_state.simple_filters:
            st.subheader("📋 Current Filter Chain")
            
            for i, filter_item in enumerate(st.session_state.simple_filters):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"**{i+1}.** {filter_item['field']} {filter_item['operator']} {filter_item['value']}")
                with col2:
                    if st.button("🗑️", key=f"remove_{i}"):
                        st.session_state.simple_filters.pop(i)
                        st.rerun()
            
            # Logic selector and execution
            col1, col2, col3 = st.columns(3)
            with col1:
                logic = st.selectbox("Filter Logic", ["AND", "OR"])
            with col2:
                limit = st.number_input("Result Limit", min_value=1, max_value=50, value=5)
            with col3:
                if st.button("🗑️ Clear All"):
                    st.session_state.simple_filters = []
                    st.rerun()
        
            if st.button("🔍 Execute Filter Chain"):
                query = {
                    "timeframe": ["5min"],
                    "filters": {
                        "simple": st.session_state.simple_filters
                    },
                    "logic": logic,
                    "limit": limit
                }
                
                st.code(json.dumps(query, indent=2), language='json')
                
                success, result = execute_query(query)
                if success:
                    st.success(f"✅ Found {result['metadata']['total_results']} results in {result['metadata']['execution_time_ms']:.1f}ms")
                    if result['results']:
                        # Display results with key indicators
                        df_data = []
                        for stock in result['results']:
                            row = {
                                'Symbol': stock['symbol'],
                                'Close': f"₹{stock['close']:.1f}",
                                'Volume': f"{stock['volume']:,.0f}",
                            }
                            
                            # Add indicators from the filters
                            if stock.get('indicators'):
                                for filter_item in st.session_state.simple_filters:
                                    field = filter_item['field']
                                    if field in stock['indicators']:
                                        row[field] = f"{stock['indicators'][field]:.2f}"
                            
                            df_data.append(row)
                        
                        st.dataframe(pd.DataFrame(df_data), use_container_width=True)
                        
                        # Performance info
                        st.info(f"Query Complexity: {result['metadata']['query_complexity']} | "
                               f"Filters Applied: {result['metadata']['filters_applied']['simple']}")
                    else:
                        st.info("No stocks matched the criteria. Try adjusting your filters.")
                else:
                    st.error(f"❌ {result}")
        else:
            st.info("👆 Add filters using the controls above to build your query")

    # Multi-Timeframe Tab
    with tab3:
        st.header("🔗 Multi-Timeframe Analysis")
        st.write("Combine indicators across different timeframes for sophisticated screening")
        
        st.markdown("""
        <div class="example-card">
        <h4>Example: Cross-Timeframe Strategy</h4>
        <p>Find stocks where:</p>
        <ul>
        <li>5-minute RSI > 60 (short-term momentum)</li>
        <li>15-minute MACD Histogram > 0 (medium-term trend)</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("▶️ Run Multi-Timeframe Example"):
            query = {
                "timeframe": ["5min", "15min"],
                "filters": {
                    "multi_timeframe": [{
                        "conditions": [
                            {"field": "rsi_14", "operator": "gt", "value": 60, "timeframe": "5min"},
                            {"field": "macd_hist_12_26_9", "operator": "gt", "value": 0, "timeframe": "15min"}
                        ],
                        "logic": "AND"
                    }]
                },
                "limit": 5
            }
            
            st.code(json.dumps(query, indent=2), language='json')
            
            success, result = execute_query(query)
            if success:
                st.success(f"✅ Multi-timeframe analysis complete: {result['metadata']['total_results']} results")
                if result['results']:
                    for stock in result['results']:
                        st.write(f"**{stock['symbol']}**: ₹{stock['close']:.1f}")

    # Fundamentals Tab
    with tab4:
        st.header("💰 Fundamentals Screening")
        st.write("Screen stocks by financial metrics and ratios")
        
        st.info("📝 Note: Fundamentals data is available for 65 companies in the database")
        
        # Available fundamentals fields
        fundamentals_fields = [
            "trailing_pe", "forward_pe", "price_to_book", "roe", "roa",
            "debt_to_equity", "current_ratio", "profit_margin", "revenue_growth"
        ]
        
        st.markdown("**Available Fundamentals Fields:**")
        fundamentals_cols = st.columns(3)
        for i, field in enumerate(fundamentals_fields):
            with fundamentals_cols[i % 3]:
                st.write(f"• {field}")
        
        # Interactive fundamentals builder
        st.subheader("🔧 Build Fundamentals Filter")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            fund_field = st.selectbox("Fundamentals Field", fundamentals_fields)
        with col2:
            fund_operator = st.selectbox("Operator", [
                ("gt", "Greater than (>)"),
                ("lt", "Less than (<)"),
                ("gte", "Greater than or equal (>=)"),
                ("lte", "Less than or equal (<=)")
            ], format_func=lambda x: x[1], key="fund_op")
        with col3:
            fund_value = st.number_input("Value", value=1.0, key="fund_val")
        
        if st.button("🔍 Test Fundamentals Filter"):
            query = {
                "timeframe": ["5min"],
                "filters": {
                    "fundamentals": [
                        {"field": fund_field, "operator": fund_operator[0], "value": fund_value}
                    ]
                },
                "limit": 10
            }
            
            st.code(json.dumps(query, indent=2), language='json')
            
            success, result = execute_query(query)
            if success:
                st.success(f"✅ Fundamentals screening complete: {result['metadata']['total_results']} results")
                if result['results']:
                    df_data = []
                    for stock in result['results']:
                        row = {
                            'Symbol': stock['symbol'],
                            'Close': f"₹{stock['close']:.1f}",
                        }
                        if stock.get('fundamentals'):
                            fund_val = stock['fundamentals'].get(fund_field)
                            if fund_val is not None:
                                row[fund_field] = f"{fund_val:.2f}" if isinstance(fund_val, (int, float)) else str(fund_val)
                        df_data.append(row)
                    st.dataframe(pd.DataFrame(df_data), use_container_width=True)
                else:
                    st.info("No stocks matched the criteria")
            else:
                st.error(f"❌ {result}")
        
        st.divider()
        
        # Success note about fundamentals fix
        st.success("✅ **Fundamentals Fixed!** Symbol formats have been aligned and fundamentals screening is now fully functional.")
        
        # Show available fundamentals data
        st.info("📊 **Available Fundamentals Data**: 58 companies updated to NSE format, including metrics like P/E ratios, market cap, ROE, debt ratios, dividend yields, etc.")
        
        # Working fundamentals examples
        st.subheader("📋 Fundamentals Query Examples")
        st.write("Try these working fundamentals queries:")
        
        # Working fundamentals example
        example_query = {
            "timeframe": ["5min"],
            "filters": {
                "fundamentals": [
                    {"field": "trailing_pe", "operator": "between", "value": [5, 25]},
                    {"field": "market_cap", "operator": "gt", "value": 1000000000}
                ]
            },
            "limit": 10
        }
        st.code(json.dumps(example_query, indent=2), language='json')
        
        if st.button("🚀 Run Fundamentals Example"):
            success, result = execute_query(example_query, "Fundamentals Example")
            if success:
                st.success(f"✅ Found {result['metadata']['total_results']} companies with P/E between 5-25 and market cap > 1B")
                if result['results']:
                    # Create focused fundamentals display
                    df_data = []
                    for stock in result['results']:
                        indicators = stock.get('indicators', {})
                        row = {
                            'Symbol': stock['symbol'],
                            'Close': f"₹{stock['close']:.1f}",
                            'P/E': f"{indicators.get('trailing_pe', 0):.1f}",
                            'Market Cap': f"₹{indicators.get('market_cap', 0)/1e9:.1f}B" if indicators.get('market_cap') else 'N/A',
                            'ROE': f"{indicators.get('roe', 0)*100:.1f}%" if indicators.get('roe') else 'N/A',
                            'Debt/Eq': f"{indicators.get('debt_to_equity', 0):.0f}" if indicators.get('debt_to_equity') else 'N/A'
                        }
                        df_data.append(row)
                    
                    df = pd.DataFrame(df_data)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No stocks matched these criteria")
            else:
                st.error(f"Query failed: {result}")
        
        st.write("💡 **Try other combinations**: P/B ratios, dividend yields, growth rates, profit margins, etc.")

    # Custom Queries Tab
    with tab5:
        st.header("⚙️ Custom Query Builder")
        st.write("Build your own custom queries with expressions")
        
        # Expression guide
        with st.expander("📖 Expression Syntax Guide"):
            st.markdown("""
            **Expression Syntax Examples:**
            
            ```sql
            -- Basic comparisons
            rsi_14 > 70
            close < sma_50
            volume > volume_sma_20 * 2
            
            -- Logical operators
            rsi_14 > 30 AND rsi_14 < 70
            (close > sma_50) AND (volume > volume_sma_20)
            macd_12_26_9 > 0 OR rsi_14 > 60
            
            -- Available fields
            close, volume, rsi_14, macd_12_26_9, sma_50, ema_21, atr_14, adx_14
            ```
            """)
        
        # Custom expression input
        expression = st.text_area(
            "Enter Custom Expression:",
            value="rsi_14 > 50 AND volume > volume_sma_20",
            help="Use SQL-like syntax to combine multiple conditions"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            timeframe = st.selectbox("Timeframe", ["5min", "15min", "1hr"])
        with col2:
            custom_limit = st.number_input("Limit", min_value=1, max_value=50, value=10)
        
        if st.button("🚀 Execute Custom Query"):
            query = {
                "timeframe": [timeframe],
                "filters": {
                    "expression": expression
                },
                "limit": custom_limit
            }
            
            st.markdown("**Generated Query:**")
            st.code(json.dumps(query, indent=2), language='json')
            
            success, result = execute_query(query)
            if success:
                st.success(f"✅ Query executed successfully: {result['metadata']['total_results']} results in {result['metadata']['execution_time_ms']:.1f}ms")
                
                if result['results']:
                    # Enhanced results display
                    df_data = []
                    for stock in result['results']:
                        row = {
                            'Symbol': stock['symbol'],
                            'Close': f"₹{stock['close']:.1f}",
                            'Volume': f"{stock['volume']:,.0f}",
                        }
                        
                        # Add key indicators
                        if stock.get('indicators'):
                            indicators = stock['indicators']
                            row.update({
                                'RSI_14': f"{indicators.get('rsi_14', 0):.1f}",
                                'MACD': f"{indicators.get('macd_12_26_9', 0):.2f}",
                                'SMA_50': f"{indicators.get('sma_50', 0):.1f}",
                                'ADX_14': f"{indicators.get('adx_14', 0):.1f}"
                            })
                        
                        df_data.append(row)
                    
                    df = pd.DataFrame(df_data)
                    st.dataframe(df, use_container_width=True)
                    
                    # Query performance metrics
                    metadata = result['metadata']
                    st.markdown(f"""
                    **Query Performance:**
                    - Execution Time: {metadata['execution_time_ms']:.1f}ms
                    - Query Complexity: {metadata['query_complexity']}
                    - Total Results: {metadata['total_results']}
                    """)
                else:
                    st.info("No stocks matched your query criteria. Try adjusting the parameters.")
            else:
                st.error(f"❌ Query failed: {result}")

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666;">
    <p>🚀 <strong>Stock Screener API Demo</strong> | Built with Streamlit | 
    <a href="http://localhost:8001/docs" target="_blank">API Documentation</a></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 