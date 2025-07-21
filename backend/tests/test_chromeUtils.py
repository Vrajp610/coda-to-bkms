from unittest.mock import patch, MagicMock, call
from backend.utils import chromeUtils

@patch('backend.utils.chromeUtils.webdriver.Chrome')
@patch('backend.utils.chromeUtils.webdriver.ChromeService')
@patch('backend.utils.chromeUtils.Options')
def test_get_chrome_driver(mock_options, mock_chrome_service, mock_chrome):
    mock_options_instance = MagicMock()
    mock_options.return_value = mock_options_instance
    mock_service_instance = MagicMock()
    mock_chrome_service.return_value = mock_service_instance
    mock_chrome_instance = MagicMock()
    mock_chrome.return_value = mock_chrome_instance

    driver = chromeUtils.get_chrome_driver()

    mock_options.assert_called_once()
    assert mock_options_instance.add_experimental_option.call_count == 2
    mock_options_instance.add_experimental_option.assert_has_calls([
        call('excludeSwitches', ['enable-logging']),
        call('detach', True)
    ], any_order=True)
    mock_chrome_service.assert_called_once()
    mock_chrome.assert_called_once_with(service=mock_service_instance, options=mock_options_instance)
    assert driver == mock_chrome_instance

@patch('backend.utils.chromeUtils.webdriver.Chrome')
@patch('backend.utils.chromeUtils.webdriver.ChromeService')
@patch('backend.utils.chromeUtils.Options')
def test_get_chrome_driver_options_experimental_options_order(mock_options, mock_chrome_service, mock_chrome):
    mock_options_instance = MagicMock()
    mock_options.return_value = mock_options_instance
    mock_service_instance = MagicMock()
    mock_chrome_service.return_value = mock_service_instance
    mock_chrome_instance = MagicMock()
    mock_chrome.return_value = mock_chrome_instance

    chromeUtils.get_chrome_driver()

    calls = [
        call('excludeSwitches', ['enable-logging']),
        call('detach', True)
    ]
    mock_options_instance.add_experimental_option.assert_has_calls(calls)

@patch('backend.utils.chromeUtils.webdriver.Chrome')
@patch('backend.utils.chromeUtils.webdriver.ChromeService')
@patch('backend.utils.chromeUtils.Options')
def test_get_chrome_driver_returns_chrome_instance(mock_options, mock_chrome_service, mock_chrome):
    mock_options_instance = MagicMock()
    mock_options.return_value = mock_options_instance
    mock_service_instance = MagicMock()
    mock_chrome_service.return_value = mock_service_instance
    mock_chrome_instance = MagicMock()
    mock_chrome.return_value = mock_chrome_instance

    result = chromeUtils.get_chrome_driver()

    assert result is mock_chrome_instance

def test_get_chrome_driver_docstring():
    assert chromeUtils.get_chrome_driver.__doc__ == "Set up and return a Chrome WebDriver instance."