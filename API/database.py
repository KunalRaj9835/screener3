"""Database connection and utility functions"""

import psycopg2
import psycopg2.extras
from psycopg2.pool import ThreadedConnectionPool
from contextlib import contextmanager
import logging
from typing import Dict, List, Any, Optional
import time

from config import DATABASE_CONFIG

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Database connection manager with connection pooling"""
    
    def __init__(self):
        self.pool = None
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Initialize connection pool"""
        try:
            self.pool = ThreadedConnectionPool(
                minconn=1,
                maxconn=20,
                host=DATABASE_CONFIG["host"],
                port=DATABASE_CONFIG["port"],
                database=DATABASE_CONFIG["database"],
                user=DATABASE_CONFIG["user"],
                password=DATABASE_CONFIG["password"],
                cursor_factory=psycopg2.extras.RealDictCursor
            )
            logger.info("Database connection pool initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database pool: {e}")
            raise

    @contextmanager
    def get_connection(self):
        """Get a connection from the pool"""
        connection = None
        try:
            connection = self.pool.getconn()
            yield connection
        finally:
            if connection:
                self.pool.putconn(connection)

    @contextmanager
    def get_cursor(self):
        """Get a cursor with automatic connection management"""
        with self.get_connection() as connection:
            cursor = connection.cursor()
            try:
                yield cursor
                connection.commit()
            except Exception as e:
                connection.rollback()
                logger.error(f"Database operation failed: {e}")
                raise
            finally:
                cursor.close()

    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict]:
        """Execute a query and return results"""
        start_time = time.time()
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, params)
                results = cursor.fetchall()
                execution_time = (time.time() - start_time) * 1000
                logger.info(f"Query executed in {execution_time:.2f}ms, returned {len(results)} rows")
                return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            raise

    def execute_query_with_metadata(self, query: str, params: Optional[tuple] = None) -> Dict:
        """Execute a query and return results with metadata"""
        start_time = time.time()
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, params)
                results = cursor.fetchall()
                execution_time = (time.time() - start_time) * 1000
                
                metadata = {
                    "execution_time_ms": execution_time,
                    "row_count": len(results),
                    "query": query[:200] + "..." if len(query) > 200 else query
                }
                
                return {
                    "results": [dict(row) for row in results],
                    "metadata": metadata
                }
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise

    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("SELECT 1")
                return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False

    def get_table_info(self, table_name: str) -> List[Dict]:
        """Get information about table columns"""
        query = """
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = %s
        ORDER BY ordinal_position
        """
        return self.execute_query(query, (table_name,))

    def get_available_symbols(self, timeframe: str) -> List[str]:
        """Get list of available symbols for a timeframe"""
        from config import TIMEFRAME_TABLE_MAP
        
        table_name = TIMEFRAME_TABLE_MAP.get(timeframe)
        if not table_name:
            raise ValueError(f"Invalid timeframe: {timeframe}")
        
        # Get the latest date and get symbols from that date
        query = f"""
        SELECT DISTINCT symbol 
        FROM {table_name} 
        WHERE datetime = (
            SELECT MAX(datetime) FROM {table_name}
        )
        ORDER BY symbol
        """
        
        results = self.execute_query(query)
        return [row['symbol'] for row in results]

    def get_latest_datetime(self, timeframe: str) -> Optional[str]:
        """Get the latest datetime available for a timeframe"""
        from config import TIMEFRAME_TABLE_MAP
        
        table_name = TIMEFRAME_TABLE_MAP.get(timeframe)
        if not table_name:
            raise ValueError(f"Invalid timeframe: {timeframe}")
        
        query = f"SELECT MAX(datetime) as latest_datetime FROM {table_name}"
        results = self.execute_query(query)
        
        if results and results[0]['latest_datetime']:
            return results[0]['latest_datetime'].isoformat()
        return None

    def get_data_statistics(self, timeframe: str) -> Dict:
        """Get statistics about available data"""
        from config import TIMEFRAME_TABLE_MAP
        
        table_name = TIMEFRAME_TABLE_MAP.get(timeframe)
        if not table_name:
            raise ValueError(f"Invalid timeframe: {timeframe}")
        
        # Get basic statistics
        stats_query = f"""
        SELECT 
            COUNT(*) as total_records,
            COUNT(DISTINCT symbol) as total_symbols,
            MIN(datetime) as earliest_date,
            MAX(datetime) as latest_date
        FROM {table_name}
        """
        
        stats = self.execute_query(stats_query)[0]
        
        # Get symbol count per date for recent dates
        recent_query = f"""
        SELECT 
            datetime::date as date,
            COUNT(DISTINCT symbol) as symbol_count
        FROM {table_name}
        WHERE datetime >= (SELECT MAX(datetime) - INTERVAL '7 days' FROM {table_name})
        GROUP BY datetime::date
        ORDER BY date DESC
        LIMIT 7
        """
        
        recent_data = self.execute_query(recent_query)
        
        return {
            "total_records": stats["total_records"],
            "total_symbols": stats["total_symbols"],
            "earliest_date": stats["earliest_date"].isoformat() if stats["earliest_date"] else None,
            "latest_date": stats["latest_date"].isoformat() if stats["latest_date"] else None,
            "recent_symbol_counts": recent_data
        }

    def close(self):
        """Close all connections in the pool"""
        if self.pool:
            self.pool.closeall()
            logger.info("Database connection pool closed")

# Global database manager instance
db_manager = DatabaseManager()

def get_db_manager() -> DatabaseManager:
    """Get the global database manager instance"""
    return db_manager

def close_db_connections():
    """Close all database connections"""
    global db_manager
    if db_manager:
        db_manager.close() 