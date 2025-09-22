import asyncio
import types
import sys
import pytest
import backend.utils.telegramUtils as telegram_utils


@pytest.fixture(autouse=True)
def stub_telegram_module():
    fake_module = types.ModuleType("telegram")

    class FakeBot:
        def __init__(self, token):
            self.token = token
            self.sent = []

        async def send_message(self, chat_id, text):
            await asyncio.sleep(0)
            self.sent.append({"chat_id": chat_id, "text": text})

    fake_module.Bot = FakeBot
    sys.modules["telegram"] = fake_module
    try:
        yield
    finally:
        sys.modules.pop("telegram", None)


@pytest.mark.asyncio
async def test_success_when_token_and_chat_id_are_provided(monkeypatch):
    monkeypatch.setattr(telegram_utils, "get_config_value", object())
    ok = await telegram_utils.send_telegram_message("hello world", token="T0K3N", chat_id="12345")
    assert ok is True


@pytest.mark.asyncio
async def test_get_config_value_called_and_returns_none(monkeypatch):
    calls = []
    def fake_get_config_value(key):
        calls.append(key)
        return None
    monkeypatch.setattr(telegram_utils, "get_config_value", fake_get_config_value)
    with pytest.raises(ValueError, match="TOKEN or CHAT_ID is not set"):
        await telegram_utils.send_telegram_message("msg", token="ONLY_TOKEN")
    assert calls == ["MAIN_GROUP_TELEGRAM_CHAT_ID"]


@pytest.mark.asyncio
async def test_success_when_using_env_via_get_config_value(monkeypatch):
    requested = []
    def fake_get_config_value(key: str):
        requested.append(key)
        return {
            "MAIN_GROUP_TELEGRAM_TOKEN": "ENV_TOKEN",
            "MAIN_GROUP_TELEGRAM_CHAT_ID": "ENV_CHAT",
        }.get(key)
    monkeypatch.setattr(telegram_utils, "get_config_value", fake_get_config_value)
    ok = await telegram_utils.send_telegram_message("env-backed message")
    assert ok is True
    assert requested == ["MAIN_GROUP_TELEGRAM_TOKEN", "MAIN_GROUP_TELEGRAM_CHAT_ID"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "arg_token,arg_chat,env_token,env_chat,should_raise",
    [
        (None, "C", None, "IGN", True),
        ("T", None, "IGN", None, True),
        (None, None, None, None, True),
        (None, None, "ENV_T", "ENV_C", False),
        ("ARG_T", None, "IGN", None, True),
        (None, "ARG_C", None, "IGN", True),
    ],
)
async def test_missing_token_or_chat_paths(monkeypatch, arg_token, arg_chat, env_token, env_chat, should_raise):
    def fake_get_config_value(key: str):
        return {
            "MAIN_GROUP_TELEGRAM_TOKEN": env_token,
            "MAIN_GROUP_TELEGRAM_CHAT_ID": env_chat,
        }.get(key)
    monkeypatch.setattr(telegram_utils, "get_config_value", fake_get_config_value)
    if should_raise:
        with pytest.raises(ValueError, match="TOKEN or CHAT_ID is not set"):
            await telegram_utils.send_telegram_message("x", token=arg_token, chat_id=arg_chat)
    else:
        ok = await telegram_utils.send_telegram_message("x", token=arg_token, chat_id=arg_chat)
        assert ok is True


@pytest.mark.asyncio
async def test_bot_send_message_exception_returns_false(monkeypatch):
    class RaisingBot:
        def __init__(self, token): self.token = token
        async def send_message(self, chat_id, text): raise RuntimeError("network down")
    fake_module = sys.modules["telegram"]
    monkeypatch.setattr(fake_module, "Bot", RaisingBot, raising=True)
    ok = await telegram_utils.send_telegram_message("will fail", token="T", chat_id="C")
    assert ok is False


@pytest.mark.asyncio
async def test_empty_message_is_allowed(monkeypatch):
    recorded = {}
    class RecordingBot:
        def __init__(self, token): self.token = token
        async def send_message(self, chat_id, text):
            recorded["chat_id"] = chat_id
            recorded["text"] = text
            await asyncio.sleep(0)
    sys.modules["telegram"].Bot = RecordingBot
    ok = await telegram_utils.send_telegram_message("", token="TOK", chat_id="CID")
    assert ok is True
    assert recorded == {"chat_id": "CID", "text": ""}