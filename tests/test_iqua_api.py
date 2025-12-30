import pytest
from requests.exceptions import ConnectionError, HTTPError
from unittest.mock import patch, Mock

from iqua_api import IquaApi


@patch("requests.post")
@patch("requests.get")
def test_get_device_data_success(mock_get, mock_post):
    mock_post.return_value = Mock(
        status_code=200,
        json=lambda: {"access_token": "123somerandomtoken123"},
        raise_for_status=lambda: None,
    )

    mock_get.return_value = Mock(
        status_code=200,
        json=lambda: {"device": {"properties": {}}},
        raise_for_status=lambda: None,
    )

    api = IquaApi("user", "pass", "dev")
    data = api.get_device_data()

    assert "device" in data

@patch("requests.post")
@patch("requests.get")
def test_401_then_success(mock_get, mock_post):
    mock_post.return_value = Mock(
        status_code=200,
        json=lambda: {"access_token": "123somerandomtoken123"},
        raise_for_status=lambda: None,
    )

    error_response = Mock(status_code=401, text="Unauthorized")
    http_error = HTTPError(response=error_response)

    mock_get.side_effect = [
        http_error,
        Mock(
            status_code=200,
            json=lambda: {"device": {"properties": {}}},
            raise_for_status=lambda: None,
        ),
    ]

    api = IquaApi("user", "pass", "dev")
    data = api.get_device_data()

    assert "device" in data

@patch("requests.post")
@patch("requests.get")
def test_401_then_401_again(mock_get, mock_post):
    mock_post.return_value = Mock(
        status_code=200,
        json=lambda: {"access_token": "123somerandomtoken123"},
        raise_for_status=lambda: None,
    )

    error_response = Mock(status_code=401, text="Unauthorized")
    http_error = HTTPError(response=error_response)

    mock_get.side_effect = [
        http_error,
        http_error,
    ]

    api = IquaApi("user", "pass", "dev")

    with pytest.raises(HTTPError):
        data = api.get_device_data()
        assert "device" not in data

@patch("requests.post")
@patch("requests.get")
def test_500_raises(mock_get, mock_post):
    mock_post.return_value = Mock(
        status_code=200,
        json=lambda: {"access_token": "123somerandomtoken123"},
        raise_for_status=lambda: None,
    )

    mock_get.side_effect = HTTPError(response=Mock(status_code=500, text="Server error"))

    api = IquaApi("user", "pass", "dev")

    with pytest.raises(HTTPError):
        data = api.get_device_data()
        assert "device" not in data


@patch("requests.post")
@patch("requests.get")
def test_network_error(mock_get, mock_post):
    mock_post.return_value = Mock(
        status_code=200,
        json=lambda: {"access_token": "123somerandomtoken123"},
        raise_for_status=lambda: None,
    )

    mock_get.side_effect = ConnectionError("Connection error")

    api = IquaApi("user", "pass", "dev")

    with pytest.raises(ConnectionError):
        data = api.get_device_data()
        assert "device" not in data


@patch("requests.post")
@patch("requests.get")
def test_invalid_user_password(mock_get, mock_post):
    error_response = Mock(status_code=401, text="Invalid email or password")
    mock_post.return_value = Mock(
        raise_for_status=Mock(side_effect=HTTPError(response=error_response)),
        json=Mock(),
    )

    api = IquaApi("user", "pass", "dev")
    with pytest.raises(HTTPError):
        api.get_device_data()

    mock_get.assert_not_called()