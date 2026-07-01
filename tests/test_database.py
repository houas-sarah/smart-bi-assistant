"""
Tests for the safe database layer (database.NorthwindDB).

These run fully offline against the bundled northwind.db — no LLM / network.
"""

import pandas as pd
import pytest

from database import NorthwindDB


@pytest.fixture(scope="module")
def db():
    return NorthwindDB("northwind.db")


# --- Safety validation ------------------------------------------------------

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
    ],
)
def test_validate_rejects_write_operations(db, sql):
    ok, _ = db.validate_query(sql)
    assert ok is False


@pytest.mark.parametrize(
    "sql",
    [
        "SELECT * FROM Customers LIMIT 5",
        "  select CompanyName from Customers  ",
        "WITH t AS (SELECT 1) SELECT * FROM t",
    ],
)
def test_validate_accepts_read_only(db, sql):
    ok, _ = db.validate_query(sql)
    assert ok is True


def test_validate_rejects_non_select(db):
    ok, _ = db.validate_query("PRAGMA table_info(Customers)")
    assert ok is False


# --- Query execution --------------------------------------------------------

def test_execute_valid_query_returns_dataframe(db):
    df, err = db.execute_query("SELECT CompanyName FROM Customers LIMIT 3")
    assert err is None
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 3
    assert "CompanyName" in df.columns


def test_execute_invalid_sql_returns_error(db):
    df, err = db.execute_query("SELECT * FROM TableThatDoesNotExist")
    assert df is None
    assert err is not None
