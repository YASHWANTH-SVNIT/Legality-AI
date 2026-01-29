import sqlite3
from contextlib import contextmanager
import os
import logging

logger = logging.getLogger(__name__)

# Get the absolute path to the database
DB_DIR = os.path.join(os.path.dirname(__file__), '../../data')
DB_PATH = os.path.join(DB_DIR, 'legality_ai.db')

@contextmanager
def get_db_connection():
    """
    Context manager for database connections.
    Automatically handles commit/rollback and connection cleanup.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        conn.close()

def init_database():
    """
    Initialize database with schema from schema.sql
    Creates tables if they don't exist.
    """
    try:
        # Ensure data directory exists
        os.makedirs(DB_DIR, exist_ok=True)
        
        # Read schema file
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        # Execute schema
        with get_db_connection() as conn:
            conn.executescript(schema_sql)
        
        logger.info(f"✅ Database initialized successfully at {DB_PATH}")
        return True
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise

def get_db_stats():
    """Get database statistics"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            # Count records in each table
            tables = ['analyses', 'feedback', 'threshold_adjustments', 'verified_clauses', 'system_metrics']
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                stats[f"{table}_count"] = cursor.fetchone()[0]
            
            # Database file size
            if os.path.exists(DB_PATH):
                stats['db_size_mb'] = round(os.path.getsize(DB_PATH) / (1024 * 1024), 2)
            
            return stats
    except Exception as e:
        logger.error(f"❌ Failed to get DB stats: {e}")
        return {"error": str(e)}

def execute_query(query: str, params: tuple = None, fetch_one: bool = False):
    """
    Execute a SQL query and return results
    
    Args:
        query: SQL query string
        params: Query parameters (optional)
        fetch_one: If True, return only one result
    
    Returns:
        Query results as list of dicts (or single dict if fetch_one=True)
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if query.strip().upper().startswith('SELECT'):
                if fetch_one:
                    row = cursor.fetchone()
                    return dict(row) if row else None
                else:
                    return [dict(row) for row in cursor.fetchall()]
            else:
                # For INSERT/UPDATE/DELETE
                return cursor.lastrowid
    except Exception as e:
        logger.error(f"❌ Query execution failed: {e}")
        raise
