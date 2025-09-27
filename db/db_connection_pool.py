import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from contextlib import asynccontextmanager
import asyncio
import logging

logger = logging.getLogger(__name__)

DB_URL = "postgresql+asyncpg://postgres:password@localhost:5432/postgres"

# create db engine
def get_engine():
    return create_async_engine(DB_URL, 
                               echo=True,
                               pool_size=10,
                            )

@asynccontextmanager
async def get_conn(db_engine):
    conn = None

    try:
        conn = await db_engine.connect()
        logger.info("DB connection opened")
        yield conn
    # capture query, connection pool timeouts (SQLAlchemyError), 
    # database timeouts errors (asyncio),
    # OS level errors, including file I/O, permission issues, and low-level socket failures network related failures 
    # like refused connections, broken pipes, or unreachable hosts(OSerror)
    except SQLAlchemyError as e:
        logger.error("Invalid SQL syntax")
        raise
    except (OSError, asyncio.TimeoutError) as e:
        logger.error("Database connection failed")
        raise
    except Exception as e:
        logger.error(f"Unexpected DB error!")  
        raise
    finally:
        if conn is not None:
            await conn.close()
            logger.info("DB connection closed")

# testing connection
if __name__ == "__main__":
    db_engine = get_engine()
    async def test_connection():
        async with get_conn(db_engine) as conn:
            result = await conn.execute(text("SELECT NOW()"))
            current_time = result.scalar()
            print(f"✅ Connected! Current time: {current_time}")

    asyncio.run(test_connection())

