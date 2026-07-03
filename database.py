"""
Database handler for the Northwind database.

Two layers of safety:
  1. Every query is validated by sql_guard.check_sql (sqlglot AST parsing) — only
     a single, read-only statement is accepted.
  2. Queries run over a strictly read-only SQLite connection (mode=ro), so even a
     query that somehow slipped past validation physically cannot modify the data.
"""

import sqlite3
from pathlib import Path
from typing import Tuple, Optional

import pandas as pd

from sql_guard import check_sql


class NorthwindDB:
    """Handler for the Northwind trading-company database."""

    def __init__(self, db_path: str = "northwind.db"):
        self.db_path = db_path
        self._verify_connection()

    def _connect(self) -> sqlite3.Connection:
        """Open a strictly read-only connection to the database."""
        uri = Path(self.db_path).resolve().as_uri() + "?mode=ro"
        return sqlite3.connect(uri, uri=True)

    def _verify_connection(self):
        """Confirm the database is reachable at startup."""
        try:
            conn = self._connect()
            count = conn.execute("SELECT COUNT(*) FROM Customers").fetchone()[0]
            conn.close()
            print(f"Database connected: {count} customers found")
        except Exception as e:
            raise Exception(f"Database error: {str(e)}")

    def execute_query(self, sql: str) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
        """Validate, then run a read-only query. Returns (DataFrame, error)."""
        is_safe, reason = self.validate_query(sql)
        if not is_safe:
            return None, reason
        try:
            conn = self._connect()
            df = pd.read_sql_query(sql, conn)
            conn.close()
            return df, None
        except Exception as e:
            return None, str(e)

    def validate_query(self, sql: str) -> Tuple[bool, str]:
        """Return (is_safe, reason). Only a single read-only statement passes."""
        return check_sql(sql)


# Quick manual check
if __name__ == "__main__":
    print("Testing NorthwindDB...")
    db = NorthwindDB()
    results, error = db.execute_query("SELECT CompanyName, Country FROM Customers LIMIT 5")
    if error:
        print(f"Error: {error}")
    else:
        print("\nSample Customers:")
        print(results)
