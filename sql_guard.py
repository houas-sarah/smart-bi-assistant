"""
SQL safety guard.

Instead of matching keywords in a string (easy to fool and prone to false
positives), this parses the candidate SQL into a syntax tree with sqlglot and
only allows a single, read-only statement — SELECT / WITH / UNION and friends.
Anything that writes, changes schema, or that we can't parse is rejected.
"""

from typing import Tuple

import sqlglot
from sqlglot import expressions as exp

# Statement types that only read data.
_ALLOWED_ROOTS = (exp.Select, exp.Union, exp.Except, exp.Intersect, exp.Subquery)

# Node types that write data, change schema, or run arbitrary commands.
# Built by name so the module still imports on older/newer sqlglot versions.
_FORBIDDEN = tuple(
    getattr(exp, name)
    for name in (
        "Insert", "Update", "Delete", "Merge",
        "Drop", "Create", "Alter", "TruncateTable",
        "Command", "Set", "Pragma", "Attach",
    )
    if hasattr(exp, name)
)


def _parse(sql: str):
    """Parse with the SQLite dialect, falling back to a lenient parse so that
    valid queries using backtick identifiers (which SQLite accepts) still pass."""
    try:
        return sqlglot.parse(sql, read="sqlite")
    except Exception:
        return sqlglot.parse(sql)  # dialect-agnostic fallback


def check_sql(sql: str) -> Tuple[bool, str]:
    """Return ``(is_safe, reason)``.

    Safe means: exactly one statement, and it only reads data.
    """
    if not sql or not sql.strip():
        return False, "Empty query."

    try:
        statements = [s for s in _parse(sql) if s is not None]
    except Exception as exc:
        return False, f"Could not parse the SQL ({exc})."

    if not statements:
        return False, "No SQL statement found."
    if len(statements) > 1:
        return False, "Only a single statement is allowed."

    stmt = statements[0]

    if not isinstance(stmt, _ALLOWED_ROOTS):
        return False, "Only read-only SELECT queries are allowed."

    forbidden = stmt.find(*_FORBIDDEN) if _FORBIDDEN else None
    if forbidden is not None:
        return False, f"Forbidden operation: {forbidden.key.upper()}."

    return True, "Query is read-only and safe."
