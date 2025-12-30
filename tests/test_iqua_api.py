import pytest
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
