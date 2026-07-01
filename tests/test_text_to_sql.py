"""
Tests for the full text-to-SQL flow with the LLM call mocked out.

`call_llm_for_sql` is replaced with a fake so we can verify that
`text_to_sql` correctly cleans and validates whatever the model returns —
without any network access or API key.
"""

import pytest

import query_engine as qe


def test_text_to_sql_cleans_fenced_output(monkeypatch):
    monkeypatch.setattr(
        qe, "call_llm_for_sql",
        lambda q: "```sql\nSELECT CompanyName FROM Customers;\n```",
    )
    assert qe.text_to_sql("list customers") == "SELECT CompanyName FROM Customers;"


def test_text_to_sql_extracts_query_from_chatter(monkeypatch):
    monkeypatch.setattr(
        qe, "call_llm_for_sql",
        lambda q: "Sure, here you go:\nSELECT Country FROM Customers;\nHope this helps!",
    )
    assert qe.text_to_sql("countries") == "SELECT Country FROM Customers;"


def test_text_to_sql_rejects_non_select(monkeypatch):
    monkeypatch.setattr(qe, "call_llm_for_sql", lambda q: "DELETE FROM Orders;")
    with pytest.raises(RuntimeError):
        qe.text_to_sql("delete everything")


def test_text_to_sql_rejects_unusable_output(monkeypatch):
    monkeypatch.setattr(qe, "call_llm_for_sql", lambda q: "I can't help with that.")
    with pytest.raises(RuntimeError):
        qe.text_to_sql("hello")
