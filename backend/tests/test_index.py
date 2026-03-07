import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
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

def test_run_bot_success(bot_input):
    attendance = [{"name": "A"}, {"name": "B"}]
    count = 2
    update_result = {
        "marked_present": ["A"],
        "not_marked": ["B"],
        "not_found_in_bkms": [],
        "sabha_held": "Yes"
    }
    with patch("backend.index.format_data", return_value=(attendance, count)), \
         patch("backend.index.update_sheet", return_value=update_result):
        response = client.post("/run-bot", json=bot_input)
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "2 Kishores found in Coda"
        assert data["marked_present"] == ["A"]
        assert data["not_marked"] == ["B"]
        assert data["not_found_in_bkms"] == []

def test_run_bot_format_data_returns_str(bot_input):
    with patch("backend.index.format_data", return_value=("No data found", 0)):
        response = client.post("/run-bot", json=bot_input)
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "No data found"

def test_run_bot_update_sheet_raises(bot_input):
    attendance = [{"name": "A"}]
    count = 1
    with patch("backend.index.format_data", return_value=(attendance, count)), \
         patch("backend.index.update_sheet", side_effect=Exception("Update failed")):
        response = client.post("/run-bot", json=bot_input)
        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert "Update failed" in data["error"]

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

def test_run_bot_format_data_raises(bot_input):
    with patch("backend.index.format_data", side_effect=Exception("Format error")):
        response = client.post("/run-bot", json=bot_input)
        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert "Format error" in data["error"]

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