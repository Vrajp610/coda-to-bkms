import asyncio
import backend.utils.sendNotifications as under_test

def _fake_asyncio_run(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def _install_fixtures(monkeypatch, cfg, main_token, main_chat, calls_list):
    async def fake_send(message, token=None, chat_id=None):
        calls_list.append({"message": message, "token": token, "chat_id": chat_id})
        return True

    monkeypatch.setattr(under_test, "TELEGRAM_GROUP_CONFIG", cfg)
    monkeypatch.setattr(under_test, "MAIN_GROUP_TOKEN", main_token)
    monkeypatch.setattr(under_test, "MAIN_GROUP_CHAT_ID", main_chat)
    monkeypatch.setattr(under_test, "send_telegram_message", fake_send)
    monkeypatch.setattr(under_test.asyncio, "run", _fake_asyncio_run)


def test_only_main_when_day_none(monkeypatch):
    calls = []
    _install_fixtures(
        monkeypatch,
        cfg={"sun": {"token": "T", "chat_id": "C"}},
        main_token="MAIN_T",
        main_chat="MAIN_C",
        calls_list=calls,
    )
    under_test.send_notifications("m1", day=None)
    assert calls == [{"message": "m1", "token": "MAIN_T", "chat_id": "MAIN_C"}]


def test_only_main_when_day_empty_string(monkeypatch):
    calls = []
    _install_fixtures(
        monkeypatch,
        cfg={"sun": {"token": "T", "chat_id": "C"}},
        main_token="MT",
        main_chat="MC",
        calls_list=calls,
    )
    under_test.send_notifications("m2", day="")
    assert calls == [{"message": "m2", "token": "MT", "chat_id": "MC"}]


def test_only_main_when_day_not_in_config(monkeypatch):
    calls = []
    _install_fixtures(
        monkeypatch,
        cfg={"sun": {"token": "T", "chat_id": "C"}},
        main_token="MT",
        main_chat="MC",
        calls_list=calls,
    )
    under_test.send_notifications("m3", day="mon")
    assert calls == [{"message": "m3", "token": "MT", "chat_id": "MC"}]


def test_only_main_when_day_has_missing_token(monkeypatch):
    calls = []
    _install_fixtures(
        monkeypatch,
        cfg={"mon": {"chat_id": "C_ONLY"}},
        main_token="MT",
        main_chat="MC",
        calls_list=calls,
    )
    under_test.send_notifications("m4", day="mon")
    assert calls == [{"message": "m4", "token": "MT", "chat_id": "MC"}]


def test_only_main_when_day_has_missing_chat_id(monkeypatch):
    calls = []
    _install_fixtures(
        monkeypatch,
        cfg={"tue": {"token": "T_ONLY"}},
        main_token="MT",
        main_chat="MC",
        calls_list=calls,
    )
    under_test.send_notifications("m5", day="tue")
    assert calls == [{"message": "m5", "token": "MT", "chat_id": "MC"}]


def test_only_main_when_day_has_empty_token_or_chat(monkeypatch):
    calls = []
    _install_fixtures(
        monkeypatch,
        cfg={"wed": {"token": "", "chat_id": "C"}, "thu": {"token": "T", "chat_id": ""}},
        main_token="MT",
        main_chat="MC",
        calls_list=calls,
    )
    under_test.send_notifications("m6", day="wed")
    under_test.send_notifications("m7", day="thu")
    assert calls == [
        {"message": "m6", "token": "MT", "chat_id": "MC"},
        {"message": "m7", "token": "MT", "chat_id": "MC"},
    ]


def test_specific_then_main_with_valid_config_and_case_insensitive_day(monkeypatch):
    calls = []
    _install_fixtures(
        monkeypatch,
        cfg={"fri": {"token": "SPEC_T", "chat_id": "SPEC_C"}},
        main_token="MT",
        main_chat="MC",
        calls_list=calls,
    )
    under_test.send_notifications("m8", day="FrI")
    assert calls == [
        {"message": "m8", "token": "SPEC_T", "chat_id": "SPEC_C"},
        {"message": "m8", "token": "MT", "chat_id": "MC"},
    ]


def test_telegram_disabled_suppresses_all_sends(monkeypatch, capsys):
    calls = []
    _install_fixtures(
        monkeypatch,
        cfg={"sat": {"token": "SPEC_T", "chat_id": "SPEC_C"}},
        main_token="MT",
        main_chat="MC",
        calls_list=calls,
    )
    monkeypatch.setattr(under_test, "TELEGRAM_ENABLED", False)
    under_test.send_notifications("disabled msg", day="sat")
    assert calls == []
    captured = capsys.readouterr()
    assert "[TELEGRAM DISABLED] disabled msg" in captured.out


def test_telegram_disabled_no_day_suppresses_all_sends(monkeypatch, capsys):
    calls = []
    _install_fixtures(
        monkeypatch,
        cfg={},
        main_token="MT",
        main_chat="MC",
        calls_list=calls,
    )
    monkeypatch.setattr(under_test, "TELEGRAM_ENABLED", False)
    under_test.send_notifications("no day msg")
    assert calls == []
    captured = capsys.readouterr()
    assert "[TELEGRAM DISABLED] no day msg" in captured.out


def test_empty_message_still_sends(monkeypatch):
    calls = []
    _install_fixtures(
        monkeypatch,
        cfg={"sat": {"token": "SPEC_T", "chat_id": "SPEC_C"}},
        main_token="MT",
        main_chat="MC",
        calls_list=calls,
    )
    under_test.send_notifications("", day="sat")
    assert calls == [
        {"message": "", "token": "SPEC_T", "chat_id": "SPEC_C"},
        {"message": "", "token": "MT", "chat_id": "MC"},
    ]


def test_specific_group_failure_still_sends_main(monkeypatch, capsys):
    calls = []

    async def fake_send(message, token=None, chat_id=None):
        calls.append({"message": message, "token": token, "chat_id": chat_id})
        return token != "SPEC_T"

    monkeypatch.setattr(under_test, "TELEGRAM_GROUP_CONFIG", {"fri": {"token": "SPEC_T", "chat_id": "SPEC_C"}})
    monkeypatch.setattr(under_test, "MAIN_GROUP_TOKEN", "MT")
    monkeypatch.setattr(under_test, "MAIN_GROUP_CHAT_ID", "MC")
    monkeypatch.setattr(under_test, "send_telegram_message", fake_send)
    monkeypatch.setattr(under_test.asyncio, "run", _fake_asyncio_run)

    result = under_test.send_notifications("m9", day="Fri")
    assert calls == [
        {"message": "m9", "token": "SPEC_T", "chat_id": "SPEC_C"},
        {"message": "m9", "token": "MT", "chat_id": "MC"},
    ]
    assert result["specific_group_sent"] is False
    assert result["main_group_sent"] is True
    assert result["all_sent"] is False
    captured = capsys.readouterr()
    assert "Specific group notification failed" in captured.out


def test_main_group_failure_reports_failure(monkeypatch, capsys):
    calls = []

    async def fake_send(message, token=None, chat_id=None):
        calls.append({"message": message, "token": token, "chat_id": chat_id})
        return token != "MAIN_T"

    monkeypatch.setattr(under_test, "TELEGRAM_GROUP_CONFIG", {"sat": {"token": "SPEC_T", "chat_id": "SPEC_C"}})
    monkeypatch.setattr(under_test, "MAIN_GROUP_TOKEN", "MAIN_T")
    monkeypatch.setattr(under_test, "MAIN_GROUP_CHAT_ID", "MAIN_C")
    monkeypatch.setattr(under_test, "send_telegram_message", fake_send)
    monkeypatch.setattr(under_test.asyncio, "run", _fake_asyncio_run)

    result = under_test.send_notifications("m10", day="sat")
    assert calls == [
        {"message": "m10", "token": "SPEC_T", "chat_id": "SPEC_C"},
        {"message": "m10", "token": "MAIN_T", "chat_id": "MAIN_C"},
    ]
    assert result["specific_group_sent"] is True
    assert result["main_group_sent"] is False
    assert result["all_sent"] is False
    captured = capsys.readouterr()
    assert "Main group notification failed" in captured.out