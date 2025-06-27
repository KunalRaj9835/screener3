#!/bin/bash

echo "🚀 Starting Stock Screener API Demo Website..."
echo "📊 Make sure your API server is running on port 8001"
echo "🌐 Demo will open at: http://localhost:8501"
echo "---"

# Activate virtual environment if it exists
if [ -d "../trade_env" ]; then
    echo "Activating virtual environment..."
    source ../trade_env/bin/activate
fi

# Start Streamlit
streamlit run app.py --server.port 8501 --server.headless false 