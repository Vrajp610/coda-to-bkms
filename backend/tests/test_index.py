import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import backend.index as index_module
from backend.index import app

client = TestClient(app)

@pytest.fixture
def bot_input():
    return {
        "date": "2024-06-01",
        "group": "GroupA",
        "sabhaHeld": "Yes",
        "p2Guju": "No",
        "prepCycleDone": "Yes"
    }


@pytest.fixture(autouse=True)
def clear_trigger_token(monkeypatch):
    monkeypatch.delenv("BOT_TRIGGER_TOKEN", raising=False)

def test_run_bot_starts_background_job(bot_input, tmp_path, monkeypatch):
    monkeypatch.setattr(index_module, "JOB_DIR", tmp_path)
    attendance = [{"name": "A"}, {"name": "B"}]
    count = 2
    update_result = {
        "marked_present": 1,
        "not_marked": 1,
        "marked_present_ids": ["A"],
        "not_marked_ids": ["B"],
        "not_found_in_bkms": [],
        "sabha_held": "Yes",
    }
    with patch("backend.index.format_data", return_value=(attendance, count)), \
         patch("backend.index.update_sheet", return_value=update_result):
        response = client.post("/run-bot", json=bot_input)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "running"
        assert data["message"] == "2 Kishores found in Coda. BKMS update starting in background..."
        assert data["attendance_count"] == 2
        assert data["job_id"]

        status_response = client.get(f"/attendance-job/{data['job_id']}")
        assert status_response.status_code == 200
        status_data = status_response.json()
        assert status_data["status"] == "completed"
        assert status_data["marked_present"] == 1
        assert status_data["not_marked"] == 1
        assert status_data["marked_present_ids"] == ["A"]
        assert status_data["not_marked_ids"] == ["B"]
        assert status_data["not_found_in_bkms"] == []

def test_run_bot_format_data_returns_str(bot_input, tmp_path, monkeypatch):
    monkeypatch.setattr(index_module, "JOB_DIR", tmp_path)
    with patch("backend.index.format_data", return_value="No data found"):
        response = client.post("/run-bot", json=bot_input)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "failed"
        assert data["message"] == "No data found"
        status_response = client.get(f"/attendance-job/{data['job_id']}")
        assert status_response.status_code == 200
        assert status_response.json()["status"] == "failed"

def test_run_bot_update_sheet_raises(bot_input, tmp_path, monkeypatch):
    monkeypatch.setattr(index_module, "JOB_DIR", tmp_path)
    attendance = [{"name": "A"}]
    count = 1
    with patch("backend.index.format_data", return_value=(attendance, count)), \
         patch("backend.index.update_sheet", side_effect=Exception("Update failed")):
        response = client.post("/run-bot", json=bot_input)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "running"
        status_response = client.get(f"/attendance-job/{data['job_id']}")
        assert status_response.status_code == 200
        status_data = status_response.json()
        assert status_data["status"] == "failed"
        assert "Update failed" in status_data["error"]

def test_run_bot_invalid_input():
    invalid_input = {
        "date": "2024-06-01",
        "sabhaHeld": "Yes",
        "p2Guju": "No",
        "prepCycleDone": "Yes"
    }
    response = client.post("/run-bot", json=invalid_input)
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "BKMS backend is running"}


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_run_bot_requires_token_when_configured(bot_input, monkeypatch):
    monkeypatch.setenv("BOT_TRIGGER_TOKEN", "secret123")
    response = client.post("/run-bot", json=bot_input)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or missing trigger token"


def test_run_bot_accepts_query_token_when_configured(bot_input, monkeypatch, tmp_path):
    monkeypatch.setenv("BOT_TRIGGER_TOKEN", "secret123")
    monkeypatch.setattr(index_module, "JOB_DIR", tmp_path)
    attendance = [{"name": "A"}]
    count = 1
    with patch("backend.index.format_data", return_value=(attendance, count)), \
         patch("backend.index.update_sheet", return_value={"marked_present": 1, "not_marked": 0, "not_found_in_bkms": [], "sabha_held": "Yes"}):
        response = client.post("/run-bot?token=secret123", json=bot_input)
        assert response.status_code == 200
        assert response.json()["status"] == "running"

def test_run_bot_format_data_raises(bot_input, tmp_path, monkeypatch):
    monkeypatch.setattr(index_module, "JOB_DIR", tmp_path)
    with patch("backend.index.format_data", side_effect=Exception("Format error")):
        response = client.post("/run-bot", json=bot_input)
        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert "Format error" in data["error"]


def test_get_attendance_job_not_found(tmp_path, monkeypatch):
    monkeypatch.setattr(index_module, "JOB_DIR", tmp_path)
    response = client.get("/attendance-job/missing-job")
    assert response.status_code == 404
    assert response.json()["detail"] == "Attendance job not found"

def test_run_bot_stream_success(bot_input):
    attendance = [{"name": "A"}, {"name": "B"}]
    count = 2
    with patch("backend.index.format_data", return_value=(attendance, count)), \
         patch("backend.index.update_sheet") as mock_update_sheet, \
         patch("backend.index.write_run_log") as mock_write_log:
        def fake_update(*args, log_callback=None, **kwargs):
            log_callback("Marked A as present")
            log_callback("Marked B as present")
        mock_update_sheet.side_effect = fake_update

        response = client.post("/run-bot-stream", json=bot_input)
        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]
        body = response.text
        assert "data: 2 Kishores found in Coda" in body
        assert "data: Marked A as present" in body
        assert "data: Marked B as present" in body
        assert "data: __DONE__" in body
        mock_write_log.assert_called_once()


def test_run_bot_stream_format_data_returns_str(bot_input):
    with patch("backend.index.format_data", return_value="No data found"), \
         patch("backend.index.write_run_log"):
        response = client.post("/run-bot-stream", json=bot_input)
        assert response.status_code == 200
        body = response.text
        assert "data: No data found" in body
        assert "data: __DONE__" in body


def test_run_bot_stream_update_sheet_raises(bot_input):
    attendance = [{"name": "A"}]
    count = 1
    with patch("backend.index.format_data", return_value=(attendance, count)), \
         patch("backend.index.update_sheet", side_effect=Exception("crash")), \
         patch("backend.index.write_run_log"):
        response = client.post("/run-bot-stream", json=bot_input)
        assert response.status_code == 200
        body = response.text
        assert "ERROR: crash" in body
        assert "data: __DONE__" in body


def test_run_bot_stream_countdown_messages_pass_through_but_not_logged(bot_input):
    attendance = [{"name": "A"}]
    count = 1
    with patch("backend.index.format_data", return_value=(attendance, count)), \
         patch("backend.index.update_sheet") as mock_update_sheet, \
         patch("backend.index.write_run_log") as mock_write_log:
        def fake_update(*args, log_callback=None, **kwargs):
            log_callback("__COUNTDOWN__15")
            log_callback("real log line")
        mock_update_sheet.side_effect = fake_update

        response = client.post("/run-bot-stream", json=bot_input)
        body = response.text
        assert "data: __COUNTDOWN__15" in body

        # __COUNTDOWN__ messages should not be written to the log file
        call_args = mock_write_log.call_args
        lines_written = call_args[0][0]
        assert "__COUNTDOWN__15" not in lines_written
        assert "real log line" in lines_written


def test_run_bot_stream_invalid_input():
    response = client.post("/run-bot-stream", json={"date": "2024-06-01", "sabhaHeld": "Yes"})
    assert response.status_code == 422


def test_run_user_update_stream_success():
    with patch("backend.index.update_users") as mock_update:
        def fake_update(user_ids, log_callback=None):
            log_callback("starting")
            log_callback("done")
        mock_update.side_effect = fake_update
        response = client.post("/run-user-update-stream", json={"user_ids": ["123", "456"]})
        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]
        body = response.text
        assert "data: starting" in body
        assert "data: done" in body
        assert "data: __DONE__" in body


def test_run_user_update_stream_exception():
    with patch("backend.index.update_users", side_effect=Exception("boom")):
        response = client.post("/run-user-update-stream", json={"user_ids": ["123"]})
        assert response.status_code == 200
        body = response.text
        assert "ERROR: boom" in body
        assert "data: __DONE__" in body


def test_run_user_update_stream_invalid_input():
    response = client.post("/run-user-update-stream", json={"wrong_field": []})
    assert response.status_code == 422


# ── /run-goshthi-stream ───────────────────────────────────────────────────────

@pytest.fixture
def goshthi_input():
    return {
        "month": "January",
        "year": "2026",
        "goshthiHeld": "Yes",
        "hangout": "No",
        "workshop": "No",
    }


def test_run_goshthi_stream_success(goshthi_input):
    attendance = ["100", "200"]
    count = 2
    with patch("backend.index.format_goshthi_data", return_value=(attendance, count)), \
         patch("backend.index.update_goshthi") as mock_update, \
         patch("backend.index.write_run_log") as mock_log:
        def fake_update(*args, log_callback=None, **kwargs):
            log_callback("Updating member 100")
        mock_update.side_effect = fake_update

        response = client.post("/run-goshthi-stream", json=goshthi_input)
        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]
        body = response.text
        assert "data: 2 members found in Coda for January 2026" in body
        assert "data: Updating member 100" in body
        assert "data: __DONE__" in body
        mock_log.assert_called_once()


def test_run_goshthi_stream_format_data_returns_str(goshthi_input):
    with patch("backend.index.format_goshthi_data", return_value="Invalid month entered."), \
         patch("backend.index.write_run_log"):
        response = client.post("/run-goshthi-stream", json=goshthi_input)
        assert response.status_code == 200
        body = response.text
        assert "data: Invalid month entered." in body
        assert "data: __DONE__" in body


def test_run_goshthi_stream_update_raises(goshthi_input):
    with patch("backend.index.format_goshthi_data", return_value=(["100"], 1)), \
         patch("backend.index.update_goshthi", side_effect=Exception("goshthi crash")), \
         patch("backend.index.write_run_log"):
        response = client.post("/run-goshthi-stream", json=goshthi_input)
        assert response.status_code == 200
        body = response.text
        assert "ERROR: goshthi crash" in body
        assert "data: __DONE__" in body


def test_run_goshthi_stream_invalid_input():
    response = client.post("/run-goshthi-stream", json={"month": "January"})
    assert response.status_code == 422


def test_run_goshthi_stream_not_marked_not_found_not_logged(goshthi_input):
    with patch("backend.index.format_goshthi_data", return_value=(["100"], 1)), \
         patch("backend.index.update_goshthi") as mock_update, \
         patch("backend.index.write_run_log") as mock_write_log:
        def fake_update(*args, log_callback=None, **kwargs):
            log_callback("__NOT_MARKED__200")
            log_callback("__NOT_FOUND__300")
            log_callback("real log line")
        mock_update.side_effect = fake_update

        response = client.post("/run-goshthi-stream", json=goshthi_input)
        body = response.text
        assert "data: __NOT_MARKED__200" in body
        assert "data: __NOT_FOUND__300" in body

        lines_written = mock_write_log.call_args[0][0]
        assert "__NOT_MARKED__200" not in lines_written
        assert "__NOT_FOUND__300" not in lines_written
        assert "real log line" in lines_written


def test_run_goshthi_stream_countdown_not_logged(goshthi_input):
    with patch("backend.index.format_goshthi_data", return_value=(["100"], 1)), \
         patch("backend.index.update_goshthi") as mock_update, \
         patch("backend.index.write_run_log") as mock_write_log:
        def fake_update(*args, log_callback=None, **kwargs):
            log_callback("__COUNTDOWN__10")
            log_callback("real msg")
        mock_update.side_effect = fake_update

        response = client.post("/run-goshthi-stream", json=goshthi_input)
        body = response.text
        assert "data: __COUNTDOWN__10" in body

        lines_written = mock_write_log.call_args[0][0]
        assert "__COUNTDOWN__10" not in lines_written
        assert "real msg" in lines_written


def test_cors_headers(bot_input):
    attendance = [{"name": "A"}]
    count = 1
    update_result = {
        "marked_present": ["A"],
        "not_marked": [],
        "not_found_in_bkms": []
    }
    with patch("backend.index.format_data", return_value=(attendance, count)), \
         patch("backend.index.update_sheet", return_value=update_result):
        response = client.options("/run-bot", headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST"
        })
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers
        assert response.headers["access-control-allow-origin"] in [
            "http://localhost:3000"]
