"""FastAPI application for Stock Screener API"""

import logging
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from models import (
    ScreenerRequest, ScreenerResponse, AvailableFieldsResponse,
    AvailableTemplatesResponse, HealthCheckResponse
)
from screener_service import get_screener_service, EnhancedScreenerService
from database import close_db_connections
from config import API_CONFIG

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Stock Screener API...")
    yield
    # Shutdown
    logger.info("Shutting down Stock Screener API...")
    close_db_connections()

# Create FastAPI application
app = FastAPI(
    title=API_CONFIG["title"],
    description=API_CONFIG["description"],
    version=API_CONFIG["version"],
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_service() -> EnhancedScreenerService:
    """Dependency to get screener service"""
    return get_screener_service()

@app.post("/api/v1/screen", response_model=ScreenerResponse)
async def screen_stocks(
    request: ScreenerRequest,
    service: EnhancedScreenerService = Depends(get_service)
):
    """
    Screen stocks based on provided filters
    
    This endpoint allows you to filter stocks using various types of filters:
    - Simple filters: Basic field comparisons
    - Expression filters: SQL-like expressions for complex logic
    - Template filters: Pre-defined filter patterns
    
    Example request:
    ```json
    {
        "timeframe": "1hr",
        "filters": {
            "simple": [
                {
                    "field": "rsi_14",
                    "operator": "between",
                    "value": [30, 70]
                },
                {
                    "field": "close",
                    "operator": "gt",
                    "reference": "sma_50"
                }
            ],
            "expression": "volume > volume_sma_20 * 1.5",
            "templates": [
                {
                    "name": "bullish_macd",
                    "params": {"fast": 12, "slow": 26, "signal": 9}
                }
            ]
        },
        "logic": "AND",
        "sort": [
            {"field": "volume", "direction": "desc"}
        ],
        "pagination": {
            "limit": 50,
            "offset": 0
        }
    }
    ```
    """
    try:
        result = service.screen_stocks(request)
        return result
    except Exception as e:
        logger.error(f"Screening request failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/fields", response_model=AvailableFieldsResponse)
async def get_available_fields(service: EnhancedScreenerService = Depends(get_service)):
    """
    Get information about available fields for filtering
    
    Returns:
    - List of all available fields with their types and descriptions
    - Available timeframes
    - Available operators for filtering
    """
    try:
        fields_info = service.get_available_fields()
        return AvailableFieldsResponse(
            fields=fields_info["fields"],
            timeframes=fields_info["timeframes"],
            operators=fields_info["operators"]
        )
    except Exception as e:
        logger.error(f"Failed to get available fields: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve field information")

@app.get("/api/v1/templates", response_model=AvailableTemplatesResponse)
async def get_available_templates(service: EnhancedScreenerService = Depends(get_service)):
    """
    Get information about available filter templates
    
    Templates are pre-defined filter patterns for common screening scenarios like:
    - RSI oversold/overbought conditions
    - Moving average crossovers
    - Volume breakouts
    - MACD patterns
    - Bollinger Band squeezes
    - And many more...
    
    Each template has configurable parameters to customize the filtering logic.
    """
    try:
        templates_info = service.get_available_templates()
        return AvailableTemplatesResponse(
            templates=templates_info["templates"],
            categories=templates_info["categories"]
        )
    except Exception as e:
        logger.error(f"Failed to get available templates: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve template information")

@app.get("/api/v1/stats/{timeframe}")
async def get_data_statistics(
    timeframe: str,
    service: EnhancedScreenerService = Depends(get_service)
):
    """
    Get statistics about available data for a specific timeframe
    
    Returns information such as:
    - Total number of records
    - Number of unique symbols
    - Date range of available data
    - Recent data quality metrics
    """
    try:
        stats = service.get_data_statistics(timeframe)
        return {"status": "success", "statistics": stats}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get data statistics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve data statistics")

@app.get("/api/v1/health", response_model=HealthCheckResponse)
async def health_check(service: EnhancedScreenerService = Depends(get_service)):
    """
    Health check endpoint to verify system status
    
    Checks:
    - Database connectivity
    - Cache connectivity (if enabled)
    - Overall system health
    """
    try:
        health = service.health_check()
        return HealthCheckResponse(
            status=health["status"],
            database=health["database"],
            cache=health["cache"],
            timestamp=health["timestamp"],
            version=API_CONFIG["version"]
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return HealthCheckResponse(
            status="unhealthy",
            database="error",
            cache="error",
            timestamp="",
            version=API_CONFIG["version"]
        )

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": API_CONFIG["title"],
        "version": API_CONFIG["version"],
        "description": API_CONFIG["description"],
        "endpoints": {
            "screen": "/api/v1/screen",
            "fields": "/api/v1/fields",
            "templates": "/api/v1/templates",
            "statistics": "/api/v1/stats/{timeframe}",
            "health": "/api/v1/health",
            "docs": "/docs"
        },
        "example_timeframes": ["1min", "5min", "15min", "1hr", "4hr"],
        "documentation": "/docs"
    }

@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle ValueError exceptions"""
    return JSONResponse(
        status_code=400,
        content={"status": "error", "detail": str(exc)}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"status": "error", "detail": "Internal server error"}
    )

if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "main:app",
        host=API_CONFIG["host"],
        port=API_CONFIG["port"],
        reload=True,
        log_level="info"
    ) 