"""
Database handler for Northwind business database
Safe SQL execution with validation
"""

import sqlite3
import pandas as pd
from typing import Tuple, Optional


class NorthwindDB:
    """Handler for Northwind trading company database"""
    
    def __init__(self, db_path: str = "northwind.db"):
        self.db_path = db_path
        self._verify_connection()
    
    def _verify_connection(self):
        """Test database connection"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Customers")
            count = cursor.fetchone()[0]
            conn.close()
            print(f"Database connected: {count} customers found")
        except Exception as e:
            raise Exception(f" Database error: {str(e)}")
    
    def execute_query(self, sql: str) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
        """Execute SQL query and return results as DataFrame"""
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query(sql, conn)
            conn.close()
            return df, None
        except Exception as e:
            return None, str(e)
    
    def validate_query(self, sql: str) -> Tuple[bool, str]:
        """Check if query is safe (read-only)"""
        sql_upper = sql.upper().strip()
        
        # Forbidden operations
        forbidden = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER', 'CREATE', 'TRUNCATE']
        
        for keyword in forbidden:
            if keyword in sql_upper:
                return False, f" Forbidden operation: {keyword}"
        
        if not sql_upper.startswith('SELECT') and not sql_upper.startswith('WITH'):
            return False, "Only SELECT queries allowed"
        
        return True, " Query is safe"


# Test the database
if __name__ == "__main__":
    print("Testing NorthwindDB...")
    db = NorthwindDB()
    
    # Test query
    sql = "SELECT CompanyName, Country FROM Customers LIMIT 5"
    results, error = db.execute_query(sql)
    
    if error:
        print(f"Error: {error}")
    else:
        print("\n Sample Customers:")
        print(results)
