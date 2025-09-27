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

db_pool: ThreadedConnectionPool | None = None

# Initialize the pool
def init_pool(minconn: int = 1, maxconn: int = 10) -> None:
    global db_pool
    if db_pool is not None:
        return
    logger.info(f"Initializing DB pool with config: {DB_CONFIG}")
    try:
        db_pool = ThreadedConnectionPool(minconn=minconn, maxconn=maxconn, **DB_CONFIG)
        logger.info("Connection pool created successfully")
        # Optional: sanity check
        conn = db_pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
                cur.fetchone()
        finally:
            db_pool.putconn(conn)
    except Exception as e:
        logger.exception(f"Error creating connection pool: {e}")
        db_pool = None
        raise


# Helper functions
def get_connection():
    if db_pool is None:
        init_pool()
    return db_pool.getconn()

def release_connection(conn):
    if db_pool and conn:
        db_pool.putconn(conn)

def close_pool(conn):
    if db_pool and conn:
        db_pool.closeall(conn)

def test_connection():
    conn = None
    try:
        conn = get_connection()

        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            print(f"Test Connection Successful: {cursor.fetchone()}")

    except Exception as e:
        print(e)
        logger.error(f"DB error: {e}")
    finally:
        if conn:
            release_connection(conn)
    
if __name__ == "__main__":
    test_connection()

