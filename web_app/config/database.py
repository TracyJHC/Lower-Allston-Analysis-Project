"""
Database utilities for the ABCDC Web Application
"""
import psycopg
from config.config import Config

def get_db_connection():
    """Get database connection using configuration"""
    try:
        conn = psycopg.connect(**Config.DB_CONFIG)
        return conn
    except psycopg.Error as e:
        print(f"Database connection error: {e}")
        return None

def execute_query(query, params=None, fetch_one=False, fetch_all=True):
    """Execute a database query and return results"""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor(row_factory=psycopg.rows.dict_row)
        cursor.execute(query, params)
        
        if fetch_one:
            result = cursor.fetchone()
        elif fetch_all:
            result = cursor.fetchall()
        else:
            result = None
            
        conn.close()
        return result
    except psycopg.Error as e:
        print(f"Database query error: {e}")
        conn.close()
        return None
