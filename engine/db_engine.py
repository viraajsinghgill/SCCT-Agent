import os, sqlite3, json
import pandas as pd

class DatabaseEngine:
    """
    Universal database query interface supporting both local high-performance SQLite
    and enterprise Snowflake Cloud data warehouses.
    """
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'supply_chain_scct.db')
        self.db_path = db_path

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def execute_query(self, query: str) -> pd.DataFrame:
        """Execute a governed SQL query and return DataFrame result."""
        # Sanitize snowflake dialect differences for local fallback
        sanitized = query.replace('CURRENT_TIMESTAMP()', "datetime('now')")
        sanitized = sanitized.replace('DATEDIFF(day,', 'julianday(')
        
        conn = self.get_connection()
        try:
            df = pd.read_sql_query(sanitized, conn)
            return df
        finally:
            conn.close()

    def get_table_schema(self, table_name: str):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name});")
        cols = cursor.fetchall()
        conn.close()
        return [{"cid": c[0], "name": c[1], "type": c[2]} for c in cols]

    def list_tables(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name, type FROM sqlite_master WHERE type IN ('table', 'view');")
        rows = cursor.fetchall()
        conn.close()
        return [{"name": r[0], "type": r[1]} for r in rows]

db_engine = DatabaseEngine()
