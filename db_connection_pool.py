from psycopg2.pool import ThreadedConnectionPool
import os
import logging

logger = logging.getLogger(__name__)

# Load credentials from environment variables or config
DB_CONFIG = {
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "password"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "database": os.getenv("DB_NAME", "postgres")
}

# Initialize the pool
try:
    db_pool = ThreadedConnectionPool(
        minconn=1,
        maxconn=10,
        **DB_CONFIG
    )
    if db_pool:
        print("Connection pool created successfully")
    logger.info("Connection pool created successfully")
except Exception as e:
    logger.error(f"Error creating connection pool: {e}")
    db_pool = None

# Helper functions
def get_connection():
    if db_pool:
        return db_pool.getconn()
    raise ConnectionError("Connection pool is not initialized")

def release_connection(conn):
    if db_pool and conn:
        db_pool.putconn(conn)

def close_pool():
    if db_pool:
        db_pool.closeall()

def test_connection():
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
    except Exception as e:
        logger.error(f"DB error: {e}")
    finally:
        if conn:
            release_connection(conn)
    

