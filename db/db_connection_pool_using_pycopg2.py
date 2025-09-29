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
    #test_connection()

    # get a database connection using pycopg2
    db_conn = get_connection()

    # create schema, table and index if it does not exists 
    try:
        cur = db_conn.cursor()

        #cur.execute("SELECT * FROM pg_extension WHERE extname = 'vector';")
        #print(cur.fetchall())
        cur.execute("SET search_path TO public, document;")

        # Create schema
        cur.execute("CREATE SCHEMA IF NOT EXISTS document;")
        db_conn.commit()

        # Create table
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS document.document_chunk (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            embedding       VECTOR(1536),
            chunk_text      TEXT,
            doc_metadata    JSONB,
            file_name       TEXT,
            tags            TEXT[],
            isActive        BOOLEAN,
            version         TEXT,
            created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at      TIMESTAMP
        );
        """
        cur.execute(create_table_sql)
        db_conn.commit()

        # Create index
        create_index_sql = """
        CREATE INDEX IF NOT EXISTS documents_embedding_idx
        ON document.document_chunk USING ivfflat (embedding vector_l2_ops)
        WITH (lists = 100);
        """
        cur.execute(create_index_sql)
        db_conn.commit()

    except Exception as e:
        print("Error:", e)
        db_conn.rollback()

    finally:
        cur.close()
        release_connection(db_conn)
