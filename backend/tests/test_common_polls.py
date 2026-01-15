import os
import pytest
from datetime import date, timedelta
from unittest.mock import patch, MagicMock

import pytest
from unittest.mock import patch, MagicMock
import os
from datetime import date
from backend.common_polls import (
	TelegramTarget,
	build_targets_from_env,
	next_weekday,
	format_date,
	build_questions_using_sunday_date,
	send_poll,
	send_polls_to_targets,
)


class TestTelegramTarget:
	def test_telegram_target_creation(self):
		target = TelegramTarget(name="TEST", token="123", chat_id="456")
		assert target.name == "TEST"
		assert target.token == "123"
		assert target.chat_id == "456"

	def test_telegram_target_frozen(self):
		target = TelegramTarget(name="TEST", token="123", chat_id="456")
		with pytest.raises(AttributeError):
			target.name = "NEW"


class TestBuildTargetsFromEnv:
	def test_build_targets_success(self):
		env = {
			"PREFIX1_TELEGRAM_TOKEN": "token1",
			"PREFIX1_TELEGRAM_CHAT_ID": "chat1",
			"PREFIX2_TELEGRAM_TOKEN": "token2",
			"PREFIX2_TELEGRAM_CHAT_ID": "chat2",
		}
		with patch.dict(os.environ, env, clear=True):
			targets = build_targets_from_env("PREFIX")
			assert len(targets) == 2
			assert targets[0].name == "PREFIX1"
			assert targets[1].name == "PREFIX2"

	def test_build_targets_filter_prefix(self):
		env = {
			"PROD_TELEGRAM_TOKEN": "token1",
			"PROD_TELEGRAM_CHAT_ID": "chat1",
			"DEV_TELEGRAM_TOKEN": "token2",
			"DEV_TELEGRAM_CHAT_ID": "chat2",
		}
		with patch.dict(os.environ, env, clear=True):
			targets = build_targets_from_env("PROD")
			assert len(targets) == 1
			assert targets[0].name == "PROD"

	def test_build_targets_strips_whitespace(self):
		env = {
			"PREFIX_TELEGRAM_TOKEN": "  token1  ",
			"PREFIX_TELEGRAM_CHAT_ID": "  chat1  ",
		}
		with patch.dict(os.environ, env, clear=True):
			targets = build_targets_from_env("PREFIX")
			assert targets[0].token == "token1"
			assert targets[0].chat_id == "chat1"

	def test_build_targets_no_matching_prefix(self):
		with patch.dict(os.environ, {}, clear=True):
			with pytest.raises(ValueError, match="No matching targets found"):
				build_targets_from_env("NONEXISTENT")

	def test_build_targets_missing_token(self):
		env = {"PREFIX_TELEGRAM_CHAT_ID": "chat1"}
		with patch.dict(os.environ, env, clear=True):
			with pytest.raises(ValueError):
				build_targets_from_env("PREFIX")

	def test_build_targets_missing_chat_id(self):
		env = {"PREFIX_TELEGRAM_TOKEN": "token1"}
		with patch.dict(os.environ, env, clear=True):
			with pytest.raises(ValueError):
				build_targets_from_env("PREFIX")


class TestNextWeekday:
	def test_next_weekday_same_day(self):
		test_date = date(2026, 1, 19)  # Monday
		result = next_weekday(0, from_day=test_date)
		assert result == test_date

	def test_next_weekday_future(self):
		test_date = date(2026, 1, 19)  # Monday
		result = next_weekday(2, from_day=test_date)  # Wednesday
		assert result == date(2026, 1, 21)

	def test_next_weekday_wrap_around(self):
		test_date = date(2026, 1, 23)  # Friday
		result = next_weekday(0, from_day=test_date)  # Monday
		assert result == date(2026, 1, 26)

	def test_next_weekday_today(self):
		with patch("backend.common_polls.date") as mock_date:
			mock_date.today.return_value = date(2026, 1, 19)
			result = next_weekday(0)
			assert result == date(2026, 1, 19)

	def test_next_weekday_all_days(self):
		test_date = date(2026, 1, 19)  # Monday
		for day in range(7):
			result = next_weekday(day, from_day=test_date)
			assert result.weekday() == day


class TestFormatDate:
	def test_format_date(self):
		d = date(2026, 1, 18)
		assert format_date(d) == "Jan 18, 2026"

	def test_format_date_different_months(self):
		assert format_date(date(2026, 12, 25)) == "Dec 25, 2026"
		assert format_date(date(2026, 3, 1)) == "Mar 01, 2026"


class TestBuildQuestionsUsingSundayDate:
	def test_build_questions_format(self):
		with patch("backend.common_polls.next_weekday") as mock_next:
			sunday = date(2026, 1, 18)
			mock_next.return_value = sunday
			questions = build_questions_using_sunday_date()
			assert len(questions) == 2
			assert "Was P2 in Guju?" in questions[0]
			assert "Was 2 week prep cycle utilized?" in questions[1]
			assert "(Jan 18, 2026)" in questions[0]


class TestSendPoll:
	@patch("backend.common_polls.requests.post")
	def test_send_poll_success(self, mock_post):
		mock_response = MagicMock()
		mock_response.json.return_value = {"ok": True, "result": {"poll_id": "123"}}
		mock_post.return_value = mock_response

		send_poll("token123", "chat456", "Test question?")
		
		mock_post.assert_called_once()
		args, kwargs = mock_post.call_args
		assert "token123" in args[0]
		assert kwargs["json"]["chat_id"] == "chat456"
		assert kwargs["json"]["question"] == "Test question?"
		assert kwargs["json"]["options"] == ["Yes", "No"]
		assert kwargs["timeout"] == 25

	@patch("backend.common_polls.requests.post")
	def test_send_poll_http_error(self, mock_post):
		mock_post.return_value.raise_for_status.side_effect = Exception("HTTP Error")
		
		with pytest.raises(Exception):
			send_poll("token123", "chat456", "Test question?")

	@patch("backend.common_polls.requests.post")
	def test_send_poll_telegram_error(self, mock_post):
		mock_response = MagicMock()
		mock_response.json.return_value = {"ok": False, "description": "Bad request"}
		mock_post.return_value = mock_response

		with pytest.raises(RuntimeError, match="Telegram API error"):
			send_poll("token123", "chat456", "Test question?")


class TestSendPollsToTargets:
	@patch("backend.common_polls.send_poll")
	@patch("backend.common_polls.build_questions_using_sunday_date")
	def test_send_polls_to_targets(self, mock_questions, mock_send):
		mock_questions.return_value = ["Q1?", "Q2?"]
		targets = [
			TelegramTarget(name="TARGET1", token="token1", chat_id="chat1"),
			TelegramTarget(name="TARGET2", token="token2", chat_id="chat2"),
		]
		
		with patch("builtins.print") as mock_print:
			send_polls_to_targets(targets)
		
		assert mock_send.call_count == 4  # 2 targets * 2 questions
		assert mock_print.call_count == 2

	@patch("backend.common_polls.send_poll")
	@patch("backend.common_polls.build_questions_using_sunday_date")
	def test_send_polls_to_targets_single(self, mock_questions, mock_send):
		mock_questions.return_value = ["Q1?"]
		targets = [TelegramTarget(name="TARGET1", token="token1", chat_id="chat1")]
		
		send_polls_to_targets(targets)
		
		mock_send.assert_called_once_with("token1", "chat1", "Q1?")