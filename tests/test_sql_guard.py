"""
Tests for the sqlglot-based SQL safety guard (sql_guard.check_sql).

These run fully offline — no database, no LLM, no network.
"""

import pytest

from sql_guard import check_sql


# --- Allowed: single read-only statements ----------------------------------

@pytest.mark.parametrize(
    "sql",
    [
        "SELECT * FROM Customers LIMIT 5",
        "  select CompanyName from Customers  ",
        "WITH t AS (SELECT 1 AS n) SELECT * FROM t",
        "SELECT 1 UNION SELECT 2",
        # Real LLM output: backtick-quoted table name with a space (SQLite accepts it)
        "SELECT SUM(od.UnitPrice * od.Quantity) AS r "
        "FROM `Order Details` od LIMIT 5",
    ],
)
def test_allows_read_only_queries(sql):
    ok, _ = check_sql(sql)
    assert ok is True


def test_allows_word_that_looks_dangerous_inside_a_string():
    # The old keyword check rejected this because the literal contains "drop".
    # AST parsing correctly sees it is just a harmless SELECT.
    ok, _ = check_sql("SELECT CompanyName FROM Customers WHERE CompanyName = 'Drop Shop'")
    assert ok is True


# --- Blocked: writes, DDL, commands ----------------------------------------

@pytest.mark.parametrize(
    "sql",
    [
        "DROP TABLE Customers",
        "DELETE FROM Orders",
        "INSERT INTO Customers VALUES (1)",
        "UPDATE Products SET UnitPrice = 0",
        "ALTER TABLE Orders ADD COLUMN x INT",
        "CREATE TABLE hack (id INT)",
        "TRUNCATE TABLE Orders",
        "PRAGMA table_info(Customers)",
    ],
)
def test_blocks_write_and_ddl(sql):
    ok, _ = check_sql(sql)
    assert ok is False


# --- Blocked: injection / multiple statements ------------------------------

def test_blocks_multiple_statements():
    ok, reason = check_sql("SELECT 1; DROP TABLE Customers")
    assert ok is False
    assert "single" in reason.lower()


@pytest.mark.parametrize("sql", ["", "   ", "this is not sql"])
def test_blocks_empty_or_garbage(sql):
    ok, _ = check_sql(sql)
    assert ok is False
