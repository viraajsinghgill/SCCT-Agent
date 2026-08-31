"""
db_engine.py — Dual-mode database adapter for SCCT Agent
  • Local mode  : SQLite (always available, no credentials needed)
  • Cloud mode  : Snowflake (activated when SNOWFLAKE_ACCOUNT env var is set)

.env format supported: PowerShell  $env:KEY = "VALUE"
                        Standard    KEY=VALUE
"""

import os
import re
import sqlite3
import json
import pandas as pd

# ── optional Snowflake connector (graceful fallback if not installed) ──────────
try:
    import snowflake.connector
    _snowflake_connector = snowflake.connector
    _SNOWFLAKE_AVAILABLE = True
except Exception:
    _snowflake_connector = None
    _SNOWFLAKE_AVAILABLE = False


# ── .env loader that handles PowerShell $env:KEY = "VALUE" syntax ─────────────
def _load_env(env_file='.env'):
    """Parse .env file supporting both standard KEY=VALUE and PowerShell $env:KEY = "VALUE"."""
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), env_file)
    if not os.path.exists(env_path):
        return
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            # PowerShell:  $env:KEY = "VALUE"  or  $env:KEY="VALUE"
            m = re.match(r'\$env:(\w+)\s*=\s*["\']?([^"\']+)["\']?', line)
            if m:
                os.environ.setdefault(m.group(1).strip(), m.group(2).strip())
                continue
            # Standard:  KEY=VALUE  or  KEY="VALUE"
            m = re.match(r'^([A-Z_][A-Z0-9_]*)\s*=\s*["\']?([^"\']*)["\']?$', line)
            if m:
                os.environ.setdefault(m.group(1).strip(), m.group(2).strip())


_load_env()  # run once at import time


# ─────────────────────────────────────────────────────────────────────────────
class DatabaseEngine:
    """
    Universal database query interface.
    
    Priority:
      1. Snowflake  — when SNOWFLAKE_ACCOUNT is set and connector is installed
      2. SQLite     — local fallback (always works)
    """

    def __init__(self, db_path=None):
        base_dir = os.path.dirname(os.path.dirname(__file__))
        if db_path is None:
            db_path = os.path.join(base_dir, 'data', 'supply_chain_scct.db')
        self.db_path = db_path

        self._sf_account   = os.environ.get('SNOWFLAKE_ACCOUNT', '').strip()
        self._sf_user      = os.environ.get('SNOWFLAKE_USER', '').strip()
        self._sf_password  = os.environ.get('SNOWFLAKE_PASSWORD', '').strip()
        self._sf_role      = os.environ.get('SNOWFLAKE_ROLE', 'ACCOUNTADMIN').strip()
        self._sf_warehouse = os.environ.get('SNOWFLAKE_WAREHOUSE', 'COMPUTE_WH').strip()
        self._sf_database  = os.environ.get('SNOWFLAKE_DATABASE', 'VS_SUPPLY_CHAIN_DB').strip()
        self._sf_schema    = os.environ.get('SNOWFLAKE_SCHEMA', 'GOLD').strip()

        # Normalise account: If not containing region or org prefix and needs region, handle properly
        # For regionless accounts (e.g. org-account like pohrwwv-ih68908), use as-is
        # If user puts only legacy locator without dot/dash, optionally add region
        if self._sf_account and '.' not in self._sf_account and '-' not in self._sf_account:
            self._sf_account = f"{self._sf_account}.central-india.azure"


        self._use_snowflake = (
            _SNOWFLAKE_AVAILABLE
            and bool(self._sf_account)
            and bool(self._sf_user)
            and bool(self._sf_password)
        )

        # Probe Snowflake at startup; fall back to SQLite if unreachable
        if self._use_snowflake:
            try:
                conn = self._get_snowflake_connection_raw()
                cur  = conn.cursor()
                cur.execute("SELECT 1")
                conn.close()
            except Exception as _probe_err:
                self._use_snowflake = False
                self._sf_probe_error = str(_probe_err)

    def set_mode(self, mode: str):
        """Explicitly select 'Snowflake' or 'SQLite'."""
        if mode == "Snowflake" and _SNOWFLAKE_AVAILABLE:
            self._use_snowflake = True
        else:
            self._use_snowflake = False

    # ── backend label ──────────────────────────────────────────────────────────
    @property
    def backend(self) -> str:
        return "Snowflake" if (self._use_snowflake and _SNOWFLAKE_AVAILABLE) else "SQLite"

    def execute_cortex_llm(self, prompt: str, model: str = "mistral-large2") -> str:
        """Call Snowflake Cortex LLM (SNOWFLAKE.CORTEX.COMPLETE) directly on Snowflake."""
        if not self._use_snowflake or not _SNOWFLAKE_AVAILABLE:
            return None
        safe_prompt = prompt.replace("'", "''")
        query = f"SELECT SNOWFLAKE.CORTEX.COMPLETE('{model}', '{safe_prompt}') AS response;"
        try:
            df = self.execute_query(query)
            if not df.empty and 'response' in df.columns:
                return df.iloc[0]['response']
        except Exception:
            pass
        return None

    # ── Snowflake helpers ─────────────────────────────────────────────────────
    def _get_snowpark_session(self):
        """Check if running inside Snowflake Native Streamlit (SiS)."""
        try:
            from snowflake.snowpark.context import get_active_session
            return get_active_session()
        except Exception:
            return None

    def _get_snowflake_connection_raw(self, login_timeout: int = 10):
        """Raw Snowflake connector call — used for both probe and queries."""
        if not _SNOWFLAKE_AVAILABLE or _snowflake_connector is None:
            raise RuntimeError("snowflake-connector-python is not installed in the active Python environment. Run: pip install snowflake-connector-python[pandas]")
        return _snowflake_connector.connect(
            account=self._sf_account,
            user=self._sf_user,
            password=self._sf_password,
            role=self._sf_role,
            warehouse=self._sf_warehouse,
            database=self._sf_database,
            schema=self._sf_schema,
            client_session_keep_alive=True,
            login_timeout=login_timeout,
            network_timeout=login_timeout,
        )

    def _get_snowflake_connection(self):
        return self._get_snowflake_connection_raw(login_timeout=30)

    def test_snowflake_connection(self) -> dict:
        """Return a dict with connection status and server info."""
        session = self._get_snowpark_session()
        if session is not None:
            return {'ok': True, 'account': 'Snowpark_SiS', 'role': 'CURRENT_ROLE', 'warehouse': 'CURRENT_WH', 'database': 'CURRENT_DB', 'schema': 'CURRENT_SCHEMA'}
        if not _SNOWFLAKE_AVAILABLE:
            return {'ok': False, 'error': 'snowflake-connector-python not installed'}
        if not (self._sf_account and self._sf_user and self._sf_password):
            return {'ok': False, 'error': 'Missing SNOWFLAKE_ACCOUNT / USER / PASSWORD env vars'}
        try:
            conn = self._get_snowflake_connection()
            cur  = conn.cursor()
            cur.execute("SELECT CURRENT_ACCOUNT(), CURRENT_ROLE(), CURRENT_WAREHOUSE(), CURRENT_DATABASE(), CURRENT_SCHEMA()")
            row = cur.fetchone()
            conn.close()
            return {
                'ok': True,
                'account':   row[0],
                'role':      row[1],
                'warehouse': row[2],
                'database':  row[3],
                'schema':    row[4],
            }
        except Exception as e:
            return {'ok': False, 'error': str(e)}

    # ── SQLite helpers ────────────────────────────────────────────────────────
    def _get_sqlite_connection(self):
        return sqlite3.connect(self.db_path)

    @staticmethod
    def _adapt_for_sqlite(query: str) -> str:
        """Translate common Snowflake SQL idioms to SQLite equivalents."""
        q = query.replace('CURRENT_TIMESTAMP()', "datetime('now')")
        q = q.replace('ILIKE', 'LIKE')
        # DATEDIFF(day, a, b) -> julianday(b) - julianday(a)  (best-effort)
        q = re.sub(
            r'DATEDIFF\s*\(\s*day\s*,\s*([^,]+),\s*([^)]+)\)',
            lambda m: f"(julianday({m.group(2).strip()}) - julianday({m.group(1).strip()}))",
            q, flags=re.IGNORECASE
        )
        return q

    # ── unified execute ───────────────────────────────────────────────────────
    def execute_query(self, query: str) -> pd.DataFrame:
        """Execute a governed SQL query and return a DataFrame."""
        # 1. Native Snowpark Session (inside Snowflake SiS)
        snowpark_session = self._get_snowpark_session()
        if snowpark_session is not None:
            try:
                sf_df = snowpark_session.sql(query)
                pdf = sf_df.to_pandas()
                pdf.columns = [c.lower() for c in pdf.columns]
                return pdf
            except Exception as e:
                # If snowpark fails, bubble error
                raise e

        # 2. Snowflake Connector (local dev connecting to remote Snowflake)
        if self._use_snowflake:
            conn = self._get_snowflake_connection()
            try:
                cur = conn.cursor()
                cur.execute(query)
                cols = [d[0].lower() for d in cur.description]
                rows = cur.fetchall()
                return pd.DataFrame(rows, columns=cols)
            finally:
                conn.close()
        else:
            sanitized = self._adapt_for_sqlite(query)
            conn = self._get_sqlite_connection()
            try:
                return pd.read_sql_query(sanitized, conn)
            finally:
                conn.close()

    # ── schema introspection ──────────────────────────────────────────────────
    def get_table_schema(self, table_name: str):
        if self._use_snowflake:
            df = self.execute_query(f"DESCRIBE TABLE {table_name}")
            return df.to_dict('records')
        else:
            conn = self._get_sqlite_connection()
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({table_name});")
            cols = cursor.fetchall()
            conn.close()
            return [{"cid": c[0], "name": c[1], "type": c[2]} for c in cols]

    def list_tables(self):
        if self._use_snowflake:
            df = self.execute_query(f"SELECT table_name, table_type FROM {self._sf_database}.information_schema.tables WHERE table_schema IN ('SILVER', 'GOLD', 'BRONZE')")
            return [{"name": r['table_name'].upper(), "type": r['table_type']} for _, r in df.iterrows()]
        else:
            conn = self._get_sqlite_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT name, type FROM sqlite_master WHERE type IN ('table', 'view');")
            rows = cursor.fetchall()
            conn.close()
            return [{"name": r[0], "type": r[1]} for r in rows]


db_engine = DatabaseEngine()
