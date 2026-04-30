from unittest.mock import patch, MagicMock, call
from backend.utils import chromeUtils

@patch('backend.utils.chromeUtils.shutil.which', return_value='/usr/bin/chromedriver')
@patch('backend.utils.chromeUtils.webdriver.Chrome')
@patch('backend.utils.chromeUtils.ChromeService')
@patch('backend.utils.chromeUtils.ChromeOptions')
def test_get_chrome_driver(mock_options, mock_chrome_service, mock_chrome, mock_which):
    mock_options_instance = MagicMock()
    mock_options.return_value = mock_options_instance
    mock_service_instance = MagicMock()
    mock_chrome_service.return_value = mock_service_instance
    mock_chrome_instance = MagicMock()
    mock_chrome.return_value = mock_chrome_instance

    driver = chromeUtils.get_chrome_driver()

    mock_options.assert_called_once()
    assert mock_options_instance.add_experimental_option.call_count == 3
    mock_options_instance.add_experimental_option.assert_has_calls([
        call('excludeSwitches', ['enable-logging']),
        call('detach', True),
        call('prefs', {
            'credentials_enable_service': False,
            'profile.password_manager_enabled': False,
            'profile.password_manager_leak_detection': False
        })
    ], any_order=True)
    mock_chrome_service.assert_called_once()
    mock_chrome.assert_called_once_with(service=mock_service_instance, options=mock_options_instance)
    assert driver == mock_chrome_instance

@patch('backend.utils.chromeUtils.shutil.which', return_value='/usr/bin/chromedriver')
@patch('backend.utils.chromeUtils.webdriver.Chrome')
@patch('backend.utils.chromeUtils.ChromeService')
@patch('backend.utils.chromeUtils.ChromeOptions')
def test_get_chrome_driver_options_experimental_options_order(mock_options, mock_chrome_service, mock_chrome, mock_which):
    mock_options_instance = MagicMock()
    mock_options.return_value = mock_options_instance
    mock_chrome_service.return_value = MagicMock()
    mock_chrome.return_value = MagicMock()

    chromeUtils.get_chrome_driver()

    calls = [
        call('excludeSwitches', ['enable-logging']),
        call('detach', True)
    ]
    mock_options_instance.add_experimental_option.assert_has_calls(calls)

@patch('backend.utils.chromeUtils.shutil.which', return_value='/usr/bin/chromedriver')
@patch('backend.utils.chromeUtils.webdriver.Chrome')
@patch('backend.utils.chromeUtils.ChromeService')
@patch('backend.utils.chromeUtils.ChromeOptions')
def test_get_chrome_driver_returns_chrome_instance(mock_options, mock_chrome_service, mock_chrome, mock_which):
    mock_options.return_value = MagicMock()
    mock_chrome_service.return_value = MagicMock()
    mock_chrome_instance = MagicMock()
    mock_chrome.return_value = mock_chrome_instance

    result = chromeUtils.get_chrome_driver()

    assert result is mock_chrome_instance

def test_get_chrome_driver_docstring():
    assert chromeUtils.get_chrome_driver.__doc__ == "Set up and return a Chrome WebDriver instance."

@patch('backend.utils.chromeUtils.shutil.which', return_value=None)
@patch('backend.utils.chromeUtils.webdriver.Chrome')
@patch('backend.utils.chromeUtils.ChromeOptions')
def test_get_chrome_driver_no_chromedriver_in_path(mock_options, mock_chrome, mock_which):
    """When chromedriver is not in PATH, Chrome is created without a Service."""
    mock_options_instance = MagicMock()
    mock_options.return_value = mock_options_instance
    mock_chrome_instance = MagicMock()
    mock_chrome.return_value = mock_chrome_instance

    result = chromeUtils.get_chrome_driver()

    mock_chrome.assert_called_once_with(options=mock_options_instance)
    assert result is mock_chrome_instance

@patch('backend.utils.chromeUtils.shutil.which', return_value='/usr/bin/chromedriver')
@patch('backend.utils.chromeUtils.ChromeService')
def test_auto_service_returns_service(mock_service, mock_which):
    mock_service.return_value = 'service'

    service = chromeUtils._auto_service()

    mock_service.assert_called_once()
    assert service == 'service'

@patch('backend.utils.chromeUtils.shutil.which', return_value=None)
def test_auto_service_returns_none_when_chromedriver_missing(mock_which):
    assert chromeUtils._auto_service() is None

@patch('backend.utils.chromeUtils.Path.exists', return_value=True)
def test_chrome_binary_returns_installation_path(mock_exists):
    assert chromeUtils._chrome_binary() == "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    mock_exists.assert_called_once()

@patch('backend.utils.chromeUtils.Path.exists', return_value=False)
def test_chrome_binary_returns_none_when_missing(mock_exists):
    assert chromeUtils._chrome_binary() is None

@patch('backend.utils.chromeUtils.shutil.which', return_value='/usr/bin/chromedriver')
@patch('backend.utils.chromeUtils.webdriver.Chrome')
@patch('backend.utils.chromeUtils.ChromeService')
@patch('backend.utils.chromeUtils.ChromeOptions')
def test_get_chrome_driver_maximize_window_exception_is_swallowed(mock_options, mock_chrome_service, mock_chrome, mock_which):
    """maximize_window() failures are silently ignored."""
    mock_options.return_value = MagicMock()
    mock_chrome_service.return_value = MagicMock()
    mock_chrome_instance = MagicMock()
    mock_chrome_instance.maximize_window.side_effect = Exception("cannot maximize")
    mock_chrome.return_value = mock_chrome_instance

    result = chromeUtils.get_chrome_driver()

    assert result is mock_chrome_instance
