#!/usr/bin/env python3
"""
Simple startup script for the Stock Screener API
"""

import os
import sys
import uvicorn
from pathlib import Path

def main():
    """Main startup function"""
    
    # Add current directory to Python path
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    
    # Set default environment variables if not set
    os.environ.setdefault("DB_HOST", "localhost")
    os.environ.setdefault("DB_PORT", "5432")
    os.environ.setdefault("DB_NAME", "postgres")
    os.environ.setdefault("DB_USER", "postgres")
    os.environ.setdefault("DB_PASSWORD", "password")
    
    print("🚀 Starting Stock Screener API...")
    print("📊 Database connection will be tested on startup")
    print("📖 API documentation available at: http://localhost:8001/docs")
    print("🔍 Example usage available at: http://localhost:8001")
    print("-" * 60)
    
    # Run the FastAPI application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    main() 