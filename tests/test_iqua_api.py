import pytest
import aiohttp
import asyncio
from unittest.mock import patch, Mock

from iqua_api import IquaApi


pytestmark = pytest.mark.asyncio


class MockAioHttpResponse:
    def __init__(self, status=200, json_data=None, message=None):
        self.status = status
        self.data = json_data
        self.message = message

    async def json(self):
        return self.data
    
    def raise_for_status(self):
        if self.status >= 400:
            raise aiohttp.ClientResponseError(
                status=self.status,
                message=self.message or "",
                headers=None,
                request_info=None,
                history=None,
            )
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc, tb):
        return False


@patch("aiohttp.ClientSession.post")
@patch("aiohttp.ClientSession.get")
async def test_get_device_data_success(mock_get, mock_post):
    mock_post.return_value = MockAioHttpResponse(json_data={"access_token": "123somerandomtoken123"})
    mock_get.return_value  = MockAioHttpResponse(json_data={"device": {"properties": {}}})

    async with aiohttp.ClientSession() as session:
        api = IquaApi(session, "user", "pass", "dev")
        data = await api.get_device_data()

    assert "device" in data

@patch("aiohttp.ClientSession.post")
@patch("aiohttp.ClientSession.get")
async def test_401_then_success(mock_get, mock_post):
    mock_post.return_value = MockAioHttpResponse(json_data={"access_token": "123somerandomtoken123"})
    mock_get.side_effect = [
        MockAioHttpResponse(status=401),
        MockAioHttpResponse(json_data={"device": {"properties": {}}}),
    ]

    async with aiohttp.ClientSession() as session:
        api = IquaApi(session, "user", "pass", "dev")
        data = await api.get_device_data()

    assert "device" in data

@patch("aiohttp.ClientSession.post")
@patch("aiohttp.ClientSession.get")
async def test_401_then_401_again(mock_get, mock_post):
    mock_post.return_value = MockAioHttpResponse(json_data={"access_token": "123somerandomtoken123"})
    mock_get.side_effect = [
        MockAioHttpResponse(status=401, message="Unauthorized"),
        MockAioHttpResponse(status=401, message="Unauthorized"),
    ]

    async with aiohttp.ClientSession() as session:
        api = IquaApi(session, "user", "pass", "dev")

        with pytest.raises(aiohttp.ClientResponseError) as ex:
            await api.get_device_data()

    error = ex.value
    assert error.status == 401
    assert error.message == "Unauthorized"

# @patch("requests.post")
# @patch("requests.get")
# def test_500_raises(mock_get, mock_post):
#     mock_post.return_value = Mock(
#         status_code=200,
#         json=lambda: {"access_token": "123somerandomtoken123"},
#         raise_for_status=lambda: None,
#     )

#     mock_get.side_effect = HTTPError(response=Mock(status_code=500, text="Server error"))

#     api = IquaApi("user", "pass", "dev")

#     with pytest.raises(HTTPError):
#         data = api.get_device_data()
#         assert "device" not in data


# @patch("requests.post")
# @patch("requests.get")
# def test_network_error(mock_get, mock_post):
#     mock_post.return_value = Mock(
#         status_code=200,
#         json=lambda: {"access_token": "123somerandomtoken123"},
#         raise_for_status=lambda: None,
#     )

#     mock_get.side_effect = ConnectionError("Connection error")

#     api = IquaApi("user", "pass", "dev")

#     with pytest.raises(ConnectionError):
#         data = api.get_device_data()
#         assert "device" not in data


# @patch("requests.post")
# @patch("requests.get")
# def test_invalid_user_password(mock_get, mock_post):
#     error_response = Mock(status_code=401, text="Invalid email or password")
#     mock_post.return_value = Mock(
#         raise_for_status=Mock(side_effect=HTTPError(response=error_response)),
#         json=Mock(),
#     )

#     api = IquaApi("user", "pass", "dev")
#     with pytest.raises(HTTPError):
#         api.get_device_data()

#     mock_get.assert_not_called()