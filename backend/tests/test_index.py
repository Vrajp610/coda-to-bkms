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


# ── helper function coverage ──────────────────────────────────────────────────

def test_split_origins_empty():
    from backend.index import _split_origins
    assert _split_origins(None) == []
    assert _split_origins("") == []


def test_split_origins_single():
    from backend.index import _split_origins
    assert _split_origins("http://example.com") == ["http://example.com"]


def test_split_origins_multiple():
    from backend.index import _split_origins
    result = _split_origins("http://a.com, http://b.com/")
    assert "http://a.com" in result
    assert "http://b.com" in result


def test_build_allowed_origins_includes_fly_app(monkeypatch):
    from backend import index as idx
    monkeypatch.setenv("FLY_APP_NAME", "my-test-app")
    origins = idx._build_allowed_origins()
    assert "https://my-test-app.fly.dev" in origins


def test_build_allowed_origins_includes_allowed_origins_env(monkeypatch):
    from backend import index as idx
    monkeypatch.setenv("ALLOWED_ORIGINS", "https://custom.com")
    origins = idx._build_allowed_origins()
    assert "https://custom.com" in origins


# ── /run-bal-mandal ───────────────────────────────────────────────────────────

@pytest.fixture
def bal_input():
    return {
        "date": "June 15",
        "day": "Saturday",
        "sabhaHeld": "Yes",
        "combinedGroups": "No",
        "smrutiTime": "Yes",
        "mukhpath": "No",
        "prepCycleDone": "Yes",
        "individualGroups": {},
    }


def test_run_bal_mandal_queues_job(bal_input, tmp_path, monkeypatch):
    monkeypatch.setattr(index_module, "JOB_DIR", tmp_path)
    with patch("backend.coda.get_bal_attendance_data", return_value=(["101"], 1)), \
         patch("backend.index.update_bal_sheet", return_value={
             "marked_present": 1, "not_marked": 0,
             "marked_present_ids": ["101"], "not_marked_ids": [],
             "not_found_in_bkms": [], "sabha_held": True,
         }):
        response = client.post("/run-bal-mandal", json=bal_input)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "queued"
    assert "job_id" in data


def test_run_bal_mandal_format_data_str(bal_input, tmp_path, monkeypatch):
    monkeypatch.setattr(index_module, "JOB_DIR", tmp_path)
    with patch("backend.coda.get_bal_attendance_data", return_value="No Bal data found"):
        response = client.post("/run-bal-mandal", json=bal_input)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "queued"


def test_run_bal_mandal_update_raises(bal_input, tmp_path, monkeypatch):
    monkeypatch.setattr(index_module, "JOB_DIR", tmp_path)
    with patch("backend.coda.get_bal_attendance_data", return_value=(["101"], 1)), \
         patch("backend.index.update_bal_sheet", side_effect=Exception("bal crash")):
        response = client.post("/run-bal-mandal", json=bal_input)
    assert response.status_code == 200


# ── /run-bal-mandal-stream ────────────────────────────────────────────────────

def test_run_bal_mandal_stream_success(bal_input):
    with patch("backend.coda.get_bal_attendance_data", return_value=(["101"], 1)), \
         patch("backend.index.update_bal_sheet") as mock_update, \
         patch("backend.index.write_run_log"):
        def fake_update(*args, log_callback=None, **kwargs):
            log_callback("Marked 101 present")
            return {"marked_present": 1, "not_marked": 0,
                    "marked_present_ids": ["101"], "not_marked_ids": [],
                    "not_found_in_bkms": [], "sabha_held": True}
        mock_update.side_effect = fake_update

        response = client.post("/run-bal-mandal-stream", json=bal_input)
        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]
        body = response.text
        assert "data: 1 Bals found in Coda" in body
        assert "data: Marked 101 present" in body
        assert "data: __DONE__" in body


def test_run_bal_mandal_stream_format_data_str(bal_input):
    with patch("backend.coda.get_bal_attendance_data", return_value="No Bal attendance"), \
         patch("backend.index.write_run_log"):
        response = client.post("/run-bal-mandal-stream", json=bal_input)
        assert response.status_code == 200
        body = response.text
        assert "data: No Bal attendance" in body
        assert "data: __DONE__" in body


def test_run_bal_mandal_stream_update_raises(bal_input):
    with patch("backend.coda.get_bal_attendance_data", return_value=(["101"], 1)), \
         patch("backend.index.update_bal_sheet", side_effect=Exception("bal stream crash")), \
         patch("backend.index.write_run_log"):
        response = client.post("/run-bal-mandal-stream", json=bal_input)
        assert response.status_code == 200
        body = response.text
        assert "ERROR: bal stream crash" in body
        assert "data: __DONE__" in body


def test_run_bal_mandal_stream_invalid_input():
    response = client.post("/run-bal-mandal-stream", json={"date": "June 15"})
    assert response.status_code == 422


# ── /run-goshthi (non-stream) ─────────────────────────────────────────────────

@pytest.fixture
def goshthi_sync_input():
    return {"month": "March", "year": "2026", "goshthiHeld": "Yes", "hangout": "No", "workshop": "No"}


def test_run_goshthi_success(goshthi_sync_input):
    with patch("backend.index.format_goshthi_data", return_value=(["100"], 1)), \
         patch("backend.index.update_goshthi", return_value={
             "marked_present": 1, "not_marked": 0,
             "not_found_in_bkms": [], "goshthi_held": True,
         }):
        response = client.post("/run-goshthi", json=goshthi_sync_input)
    assert response.status_code == 200
    data = response.json()
    assert data["marked_present"] == 1


def test_run_goshthi_format_data_str(goshthi_sync_input):
    with patch("backend.index.format_goshthi_data", return_value="Invalid month"):
        response = client.post("/run-goshthi", json=goshthi_sync_input)
    assert response.status_code == 200
    assert response.json()["message"] == "Invalid month"


def test_run_goshthi_raises(goshthi_sync_input):
    with patch("backend.index.format_goshthi_data", side_effect=Exception("goshthi err")):
        response = client.post("/run-goshthi", json=goshthi_sync_input)
    assert response.status_code == 200
    assert "error" in response.json()


# ── /run-user-update ──────────────────────────────────────────────────────────

def test_run_user_update_success():
    with patch("backend.index.update_users"):
        response = client.post("/run-user-update", json={"user_ids": ["123"]})
    assert response.status_code == 200
    assert "Processed 1" in response.json()["message"]


def test_run_user_update_raises():
    with patch("backend.index.update_users", side_effect=Exception("upd err")):
        response = client.post("/run-user-update", json={"user_ids": ["123"]})
    assert response.status_code == 200
    assert "error" in response.json()


def test_run_user_update_invalid_input():
    response = client.post("/run-user-update", json={"wrong": []})
    assert response.status_code == 422


# ── token auth on various endpoints ──────────────────────────────────────────

def test_run_bot_stream_requires_token_when_configured(bot_input, monkeypatch):
    monkeypatch.setenv("BOT_TRIGGER_TOKEN", "mock-secret")
    response = client.post("/run-bot-stream", json=bot_input)
    assert response.status_code == 401


def test_run_goshthi_stream_requires_token_when_configured(monkeypatch):
    monkeypatch.setenv("BOT_TRIGGER_TOKEN", "mock-secret")
    goshthi = {"month": "Jan", "year": "2026", "goshthiHeld": "No", "hangout": "No", "workshop": "No"}
    response = client.post("/run-goshthi-stream", json=goshthi)
    assert response.status_code == 401


def test_run_bal_mandal_stream_requires_token_when_configured(bal_input, monkeypatch):
    monkeypatch.setenv("BOT_TRIGGER_TOKEN", "mock-secret")
    response = client.post("/run-bal-mandal-stream", json=bal_input)
    assert response.status_code == 401


def test_run_user_update_stream_requires_token_when_configured(monkeypatch):
    monkeypatch.setenv("BOT_TRIGGER_TOKEN", "mock-secret")
    response = client.post("/run-user-update-stream", json={"user_ids": ["1"]})
    assert response.status_code == 401


def test_run_goshthi_requires_token_when_configured(monkeypatch):
    monkeypatch.setenv("BOT_TRIGGER_TOKEN", "mock-secret")
    goshthi = {"month": "Jan", "year": "2026", "goshthiHeld": "No", "hangout": "No", "workshop": "No"}
    response = client.post("/run-goshthi", json=goshthi)
    assert response.status_code == 401


def test_run_user_update_requires_token_when_configured(monkeypatch):
    monkeypatch.setenv("BOT_TRIGGER_TOKEN", "mock-secret")
    response = client.post("/run-user-update", json={"user_ids": ["1"]})
    assert response.status_code == 401


def test_get_attendance_job_requires_token_when_configured(monkeypatch, tmp_path):
    monkeypatch.setenv("BOT_TRIGGER_TOKEN", "mock-secret")
    response = client.get("/attendance-job/some-job")
    assert response.status_code == 401


def test_run_bal_mandal_requires_token_when_configured(bal_input, monkeypatch):
    monkeypatch.setenv("BOT_TRIGGER_TOKEN", "mock-secret")
    response = client.post("/run-bal-mandal", json=bal_input)
    assert response.status_code == 401
