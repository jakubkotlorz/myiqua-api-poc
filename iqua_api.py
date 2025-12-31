import aiohttp
import logging

_LOGGER = logging.getLogger(__name__)


class IquaApi:
    BASE_URL = "https://api.myiquaapp.com/v1"

    def __init__(self, session, email: str, passw: str, dev_id: str):
        self._session = session
        self._email = email
        self._password = passw
        self._device_id = dev_id
        self._token = None

    async def get_device_data(self) -> dict:
        max_attempts = 2
        for attempt in range(max_attempts):
            if self._token is None:
                await self._login()
            try:
                return await self._fetch_data()
            except aiohttp.ClientResponseError as e:
                if e.status == 401 and attempt < max_attempts-1:
                    _LOGGER.warning("Token expired, re-authenticating")
                    self._token = None
                    continue
                else:
                    _LOGGER.error(f"HTTP {e.status}: {e.message}")
                    raise

    async def _login(self):
        LOGIN_ENDPOINT = "/auth/login"
        payload = {
            "email": self._email,
            "password": self._password,
        }
        async with self._session.post(IquaApi.BASE_URL + LOGIN_ENDPOINT, json=payload) as resp:
            resp.raise_for_status()
            data = await resp.json()
            self._token = data["access_token"]
            _LOGGER.info(f"Logged in, token acquired ({self._token[:10]}...)")

    async def _fetch_data(self) -> dict:
        DATA_ENDPOINT = f"/devices/{self._device_id}/detail-or-summary"
        headers = {
            "Authorization": f"Bearer {self._token}",
            "User-Agent": "iqua-water-poller/0.1",
        }
        async with self._session.get(IquaApi.BASE_URL + DATA_ENDPOINT, headers=headers) as resp:
            resp.raise_for_status()
            return await resp.json()
