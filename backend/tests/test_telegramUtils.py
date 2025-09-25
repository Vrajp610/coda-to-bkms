import pytest
import sys
import types
from unittest.mock import patch, AsyncMock, MagicMock

@pytest.fixture(autouse=True)
def reload_telegramUtils():
    if "backend.utils.telegramUtils" in sys.modules:
        del sys.modules["backend.utils.telegramUtils"]
    yield

@pytest.mark.asyncio
async def test_send_telegram_message_success(monkeypatch):
    monkeypatch.setenv("MAIN_GROUP_TELEGRAM_TOKEN", "dummy_token")
    monkeypatch.setenv("MAIN_GROUP_TELEGRAM_CHAT_ID", "dummy_chat_id")

    mock_bot_instance = AsyncMock()
    telegram_mock = types.SimpleNamespace(Bot=MagicMock(return_value=mock_bot_instance))
    error_mod = types.SimpleNamespace(InvalidToken=type("InvalidToken", (Exception,), {}))
    with patch.dict(sys.modules, {"telegram": telegram_mock, "telegram.error": error_mod}):
        from backend.utils import telegramUtils
        await telegramUtils.send_telegram_message("Hello, test!")
        mock_bot_instance.send_message.assert_awaited_once_with(
            chat_id="dummy_chat_id", text="Hello, test!"
        )

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "token,chat_id",
    [
        (None, "dummy_chat_id"),
        ("dummy_token", None),
        (None, None),
        ("", "dummy_chat_id"),
        ("dummy_token", ""),
        ("", ""),
    ],
)
async def test_send_telegram_message_missing_env(monkeypatch, token, chat_id):
    if token is not None:
        monkeypatch.setenv("MAIN_GROUP_TELEGRAM_TOKEN", token)
    else:
        monkeypatch.delenv("MAIN_GROUP_TELEGRAM_TOKEN", raising=False)
    if chat_id is not None:
        monkeypatch.setenv("MAIN_GROUP_TELEGRAM_CHAT_ID", chat_id)
    else:
        monkeypatch.delenv("MAIN_GROUP_TELEGRAM_CHAT_ID", raising=False)

    telegram_mock = types.SimpleNamespace(Bot=AsyncMock())
    with patch.dict(sys.modules, {"telegram": telegram_mock}):
        from backend.utils import telegramUtils
        with pytest.raises(ValueError, match="Telegram TOKEN or CHAT_ID is not set"):
            await telegramUtils.send_telegram_message("Should fail")

@pytest.mark.asyncio
async def test_send_telegram_message_returns_false_on_error(monkeypatch):
    monkeypatch.setenv("MAIN_GROUP_TELEGRAM_TOKEN", "dummy_token")
    monkeypatch.setenv("MAIN_GROUP_TELEGRAM_CHAT_ID", "dummy_chat_id")

    mock_bot_instance = AsyncMock()
    mock_bot_instance.send_message.side_effect = RuntimeError("Telegram API error")
    telegram_mock = types.SimpleNamespace(Bot=MagicMock(return_value=mock_bot_instance))
    error_mod = types.SimpleNamespace(InvalidToken=type("InvalidToken", (Exception,), {}))
    
    with patch.dict(sys.modules, {"telegram": telegram_mock, "telegram.error": error_mod}):
        from backend.utils import telegramUtils
        result = await telegramUtils.send_telegram_message("fail message")
        assert result is False
        mock_bot_instance.send_message.assert_awaited_once_with(
            chat_id="dummy_chat_id", text="fail message"
        )

def test_load_dotenv_called(monkeypatch):
    load_dotenv_mock = MagicMock()
    telegram_mock = types.SimpleNamespace(Bot=MagicMock())
    with patch.dict(sys.modules, {"telegram": telegram_mock, "dotenv": types.SimpleNamespace(load_dotenv=load_dotenv_mock)}):
        import importlib
        import backend.utils.telegramUtils as tu
        load_dotenv_mock.assert_called_once()