import os
import pytest
from backend.utils.log_writer import write_run_log


def test_creates_file_and_returns_path(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    path = write_run_log(["line1", "line2"], "attendance/sat_k1", "2024-06-01_12-00-00.log")
    expected = os.path.join("logs", "attendance", "sat_k1", "2024-06-01_12-00-00.log")
    assert path == expected
    assert os.path.exists(path)


def test_writes_content_correctly(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    write_run_log(["hello", "world"], "user_update", "run.log")
    path = os.path.join("logs", "user_update", "run.log")
    with open(path) as f:
        content = f.read()
    assert content == "hello\nworld"


def test_creates_nested_directories(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    write_run_log([], "attendance/sunday_k2", "file.log")
    assert os.path.isdir(os.path.join("logs", "attendance", "sunday_k2"))


def test_empty_lines_writes_empty_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    path = write_run_log([], "test_dir", "empty.log")
    with open(path) as f:
        content = f.read()
    assert content == ""


def test_single_line_no_newline(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    path = write_run_log(["only line"], "test_dir", "single.log")
    with open(path) as f:
        content = f.read()
    assert content == "only line"


def test_overwrites_existing_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    write_run_log(["first run"], "test_dir", "run.log")
    write_run_log(["second run"], "test_dir", "run.log")
    path = os.path.join("logs", "test_dir", "run.log")
    with open(path) as f:
        content = f.read()
    assert content == "second run"
