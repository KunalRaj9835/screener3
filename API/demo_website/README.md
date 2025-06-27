# 🚀 Stock Screener API Demo Website

A comprehensive Streamlit-based demo website to showcase all the features of the Stock Screener API.

## ✨ Features

### 🔧 System Controls
- **API Server Management**: Start/stop the API server directly from the interface
- **Real-time Health Monitoring**: Live status of API and database
- **Quick Stats**: Database metrics and endpoint status

### 🎮 Interactive Query Examples
- **Quick Examples**: Pre-built queries you can run with one click
- **Simple Filters**: Interactive filter builder for basic queries
- **Multi-Timeframe Analysis**: Cross-timeframe strategy examples
- **Fundamentals Screening**: Financial metrics filtering
- **Custom Query Builder**: Build your own expressions with syntax guide

### 📊 Rich Results Display
- **Formatted Tables**: Clean presentation of stock data
- **Performance Metrics**: Query execution time and complexity
- **Real-time Results**: Live data from your API

## 🚀 Quick Start

### 1. Install Dependencies
```bash
# From the demo_website directory
pip install -r requirements.txt
```

### 2. Run the Demo
```bash
streamlit run app.py
```

### 3. Open in Browser
The demo will automatically open at: `http://localhost:8501`

## 🎯 How to Use

### System Setup
1. **Check API Status**: The sidebar shows current API health
2. **Start API Server**: Click the "Start API Server" button if offline
3. **Wait for Startup**: Allow 10-15 seconds for the server to initialize

### Explore Features
1. **Quick Examples Tab**: Try pre-built queries to see immediate results
2. **Simple Filters Tab**: Build basic filters interactively
3. **Multi-Timeframe Tab**: See cross-timeframe analysis in action
4. **Fundamentals Tab**: Explore financial metrics screening
5. **Custom Queries Tab**: Build advanced expressions with the syntax guide

## 📋 Example Queries Included

### Simple Technical Analysis
- High RSI stocks (momentum detection)
- Volume breakouts (unusual activity)
- Moving average filters (trend following)

### Advanced Multi-Timeframe
- Cross-timeframe momentum strategies
- RSI + MACD combinations
- Short-term + medium-term signals

### Expression Examples
```sql
-- Basic momentum
rsi_14 > 60 AND volume > volume_sma_20

-- Trend following
close > sma_50 AND macd_12_26_9 > 0

-- Oversold reversal
rsi_14 < 30 AND close > sma_21
```

## 🔧 Technical Details

### Architecture
- **Frontend**: Streamlit (Python web framework)
- **Backend**: Your Stock Screener API
- **Data**: Real-time API responses
- **Styling**: Custom CSS for professional appearance

### Dependencies
- `streamlit`: Web interface framework
- `requests`: API communication
- `pandas`: Data manipulation and display
- `psutil`: System monitoring

### File Structure
```
demo_website/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## 🎨 Customization

### Adding New Examples
Edit the `examples` list in `app.py` to add more pre-built queries:

```python
examples = [
    {
        "name": "Your Strategy Name",
        "description": "Strategy description",
        "query": {
            "timeframe": ["5min"],
            "filters": {"simple": [...]},
            "limit": 5
        }
    }
]
```

### Styling
Modify the CSS in the `st.markdown()` section to customize appearance.

### New Features
Add new tabs or sections by extending the tab structure in `main()`.

## 🐛 Troubleshooting

### API Server Won't Start
- Ensure you're in the correct directory
- Check that port 8000 is available
- Verify Python environment has all API dependencies

### No Query Results
- This is expected with limited demo data (49 symbols)
- Try different filter values or simpler conditions
- Check API logs for query execution details

### Connection Errors
- Verify API server is running on localhost:8000
- Check firewall settings
- Ensure database is accessible

## 📈 Performance

The demo is optimized for:
- **Fast Loading**: Minimal dependencies
- **Responsive UI**: Real-time status updates
- **Efficient Queries**: Cached API responses where possible
- **User Experience**: Clear error messages and loading indicators

## 🔗 Links

- **API Documentation**: http://localhost:8000/docs (when API is running)
- **Main API**: http://localhost:8000
- **Demo Interface**: http://localhost:8501

---

**Built with ❤️ using Streamlit | Showcasing the Stock Screener API** 