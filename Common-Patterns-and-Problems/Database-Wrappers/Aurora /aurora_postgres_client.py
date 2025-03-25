import psycopg2
import psycopg2.extras
from typing import List, Dict, Any, Optional
import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class AuroraPostgresClient:
    def __init__(self, dbname: str, user: str, password: str, host: str, port: int = 5432):
        self.conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port,
            cursor_factory=psycopg2.extras.RealDictCursor
        )
        self.conn.autocommit = True

    def fetch_all(self, query: str, params: Optional[List[Any]] = None) -> List[Dict[str, Any]]:
        try:
            with self.conn.cursor() as cur:
                cur.execute(query, params)
                result = cur.fetchall()
                logger.info(f"📤 Fetched {len(result)} rows.")
                return result
        except Exception as e:
            logger.error(f"❌ Error fetching rows: {e}")
            return []

    def fetch_one(self, query: str, params: Optional[List[Any]] = None) -> Optional[Dict[str, Any]]:
        try:
            with self.conn.cursor() as cur:
                cur.execute(query, params)
                result = cur.fetchone()
                logger.info("📤 Fetched 1 row.")
                return result
        except Exception as e:
            logger.error(f"❌ Error fetching single row: {e}")
            return None

    def execute(self, query: str, params: Optional[List[Any]] = None) -> bool:
        try:
            with self.conn.cursor() as cur:
                cur.execute(query, params)
                logger.info("✅ Executed query successfully.")
                return True
        except Exception as e:
            logger.error(f"❌ Error executing query: {e}")
            return False

    def bulk_insert(self, table: str, rows: List[Dict[str, Any]]) -> bool:
        if not rows:
            return True
        try:
            with self.conn.cursor() as cur:
                columns = rows[0].keys()
                values = [[row[col] for col in columns] for row in rows]
                insert_query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES %s"
                psycopg2.extras.execute_values(cur, insert_query, values)
                logger.info(f"📥 Inserted {len(rows)} rows into {table}")
                return True
        except Exception as e:
            logger.error(f"❌ Bulk insert failed: {e}")
            return False

    def close(self):
        self.conn.close()
        logger.info("🔒 Closed Aurora connection.")
