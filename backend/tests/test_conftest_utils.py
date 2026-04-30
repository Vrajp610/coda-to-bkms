import importlib.util
from pathlib import Path
from unittest.mock import MagicMock


def load_conftest_module():
    spec = importlib.util.spec_from_file_location(
        "backend_tests_conftest",
        Path(__file__).resolve().parent / "conftest.py",
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_instant_wait_until_returns_condition_value():
    conftest = load_conftest_module()
    driver = MagicMock()
    instant = conftest._instant_wait(driver, timeout=1)
    assert instant.until(lambda d: True) is True


def test_instant_wait_until_not_returns_condition_value():
    conftest = load_conftest_module()
    driver = MagicMock()
    instant = conftest._instant_wait(driver, timeout=1)
    assert instant.until_not(lambda d: False) is True


def test_instant_wait_until_handles_exception_gracefully():
    conftest = load_conftest_module()
    driver = MagicMock()
    instant = conftest._instant_wait(driver, timeout=1)

    def raising_condition(_):
        raise Exception("boom")

    assert instant.until(raising_condition) is None


def test_instant_wait_until_not_handles_exception_gracefully():
    conftest = load_conftest_module()
    driver = MagicMock()
    instant = conftest._instant_wait(driver, timeout=1)

    def raising_condition(_):
        raise Exception("boom")

    assert instant.until_not(raising_condition) is None
