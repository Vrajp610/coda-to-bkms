import pytest
import backend.utils.postgresConn as pgmod
from unittest.mock import MagicMock


def _make_conn(cur_execute_side_effect=None, fetchone_return=None, cursor_enter_side_effect=None):
    cur = MagicMock()
    if cur_execute_side_effect is not None:
        cur.execute.side_effect = cur_execute_side_effect

    cur.fetchone.return_value = fetchone_return

    cm = MagicMock()
    if cursor_enter_side_effect is not None:
        type(cm).__enter__ = MagicMock(side_effect=cursor_enter_side_effect)
    else:
        cm.__enter__.return_value = cur
    cm.__exit__.return_value = False

    conn = MagicMock()
    def _cursor(*, cursor_factory=None):
        _cursor.last_factory = cursor_factory
        return cm
    _cursor.last_factory = None
    conn.cursor.side_effect = _cursor
    return conn, cur, cm


def test_get_db_connection_calls_psycopg2_connect(monkeypatch):
    calls = {}
    def fake_connect(**kwargs):
        calls.update(kwargs)
        return "CONN"
    monkeypatch.setattr(pgmod.psycopg2, "connect", fake_connect)
    conn = pgmod.get_db_connection()
    assert conn == "CONN"
    assert calls == {
        "host": "localhost",
        "database": "bkms_values",
        "port": "5432",
        "user": "vrajpatel",
    }


def test_get_db_connection_raises_when_connect_fails(monkeypatch):
    def boom(**_):
        raise RuntimeError("connect failed")
    monkeypatch.setattr(pgmod.psycopg2, "connect", boom)
    with pytest.raises(RuntimeError, match="connect failed"):
        pgmod.get_db_connection()


def test_get_config_value_returns_value_and_uses_DictCursor(monkeypatch):
    conn, cur, cm = _make_conn(fetchone_return={"value": "SECRET"})
    monkeypatch.setattr(pgmod, "get_db_connection", lambda: conn)

    out = pgmod.get_config_value("MAIN_TOKEN")
    assert out == "SECRET"
    cur.execute.assert_called_once_with(
        "SELECT value FROM config WHERE key = %s", ("MAIN_TOKEN",)
    )
    assert conn.cursor.side_effect.last_factory is pgmod.DictCursor
    conn.close.assert_called_once()


def test_get_config_value_returns_none_when_missing(monkeypatch):
    conn, cur, cm = _make_conn(fetchone_return=None)
    monkeypatch.setattr(pgmod, "get_db_connection", lambda: conn)

    out = pgmod.get_config_value("MISSING_KEY")
    assert out is None
    cur.execute.assert_called_once()
    conn.close.assert_called_once()


def test_get_config_value_accepts_none_key_and_closes(monkeypatch):
    conn, cur, cm = _make_conn(fetchone_return=None)
    monkeypatch.setattr(pgmod, "get_db_connection", lambda: conn)

    out = pgmod.get_config_value(None)
    assert out is None
    cur.execute.assert_called_once_with(
        "SELECT value FROM config WHERE key = %s", (None,)
    )
    conn.close.assert_called_once()


def test_get_config_value_closes_on_execute_exception(monkeypatch):
    conn, cur, cm = _make_conn(cur_execute_side_effect=RuntimeError("boom"))
    monkeypatch.setattr(pgmod, "get_db_connection", lambda: conn)

    with pytest.raises(RuntimeError, match="boom"):
        pgmod.get_config_value("ANY")
    conn.close.assert_called_once()


def test_get_config_value_closes_on_cursor_enter_exception(monkeypatch):
    def enter_boom(*_):
        raise ValueError("enter failed")

    conn, cur, cm = _make_conn(cursor_enter_side_effect=enter_boom)
    monkeypatch.setattr(pgmod, "get_db_connection", lambda: conn)

    with pytest.raises(ValueError, match="enter failed"):
        pgmod.get_config_value("K")
    conn.close.assert_called_once()