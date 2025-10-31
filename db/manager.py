# db/manager.py
import logging
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import ThreadedConnectionPool
from config import DB_CONFIG

logger = logging.getLogger("food_agent")

class DatabaseManager:
    def __init__(self):
        minconn = int(DB_CONFIG.get("minconn", 1))
        maxconn = int(DB_CONFIG.get("maxconn", 10))
        self.pool = ThreadedConnectionPool(minconn=minconn, maxconn=maxconn, **DB_CONFIG)
        self.init_database()

    def init_database(self):
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS orders (
                        id SERIAL PRIMARY KEY,
                        user_id VARCHAR(100) NOT NULL,
                        items JSONB NOT NULL,
                        total_cost DECIMAL(10,2) NOT NULL,
                        status VARCHAR(50) DEFAULT 'pending',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_orders_user_id
                    ON orders(user_id, created_at DESC)
                """)
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_orders_status
                    ON orders(status, created_at DESC)
                """)
                conn.commit()
        finally:
            self.pool.putconn(conn)

    def execute_query(self, query: str, params: tuple = None, fetch: bool = True):
        logger.info(f"Executing SQL: {query} | Params: {params} | Fetch: {fetch}")
        conn = self.pool.getconn()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                try:
                    cur.execute(query, params or ())
                except Exception as e:
                    logger.error(f"SQL execution error: {e}")
                    raise
                is_write = query.strip().upper().startswith(("INSERT", "UPDATE", "DELETE"))
                if fetch:
                    result = [dict(row) for row in cur.fetchall()]
                    logger.info(f"SQL fetch result: {result}")
                    if is_write:
                        conn.commit()
                    return result
                else:
                    conn.commit()
                    if 'RETURNING' in query.upper():
                        row = cur.fetchone()
                        logger.info(f"SQL returning row: {row}")
                        return [dict(row)] if row else []
                    logger.info(f"SQL rowcount: {cur.rowcount}")
                    return cur.rowcount
        finally:
            self.pool.putconn(conn)

db_manager = DatabaseManager()
