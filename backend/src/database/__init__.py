"""
Database module for Legality AI
Handles SQLite database operations
"""

from .connection import (
    get_db_connection,
    init_database,
    get_db_stats,
    execute_query,
    DB_PATH
)

__all__ = [
    'get_db_connection',
    'init_database',
    'get_db_stats',
    'execute_query',
    'DB_PATH'
]
