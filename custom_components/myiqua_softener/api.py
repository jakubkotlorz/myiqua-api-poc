import aiohttp
import async_timeout
import logging

_LOGGER = logging.getLogger(__name__)


class IquaApiAsync:
    BASE_URL = "https://api.myiquaapp.com/v1"
    CONNECTION_TIMEOUT = 10

    def __init__(self, session, email: str, passw: str, dev_id: str):
        self._session = session
        self._email = email
        self._password = passw
        self._device_id = dev_id
        self._token = None

    async def get_device_data(self) -> dict:
        async with async_timeout.timeout(self.CONNECTION_TIMEOUT):
            max_attempts = 2

            for attempt in range(max_attempts):
                if self._token is None:
                    await self._login()

                try:
                    return await self._fetch_data()

                except aiohttp.ClientResponseError as err:
                    if err.status == 401 and attempt < max_attempts - 1:
                        self._token = None
                        continue
                    raise

    async def _login(self):
        LOGIN_ENDPOINT = "/auth/login"
        payload = {
            "email": self._email,
            "password": self._password,
        }

        async with self._session.post(
            self.BASE_URL + LOGIN_ENDPOINT, json=payload
        ) as resp:
            resp.raise_for_status()
            data = await resp.json()
            self._token = data["access_token"]
            _LOGGER.debug("MyIqua login successful")

    async def _fetch_data(self) -> dict:
        DATA_ENDPOINT = f"/devices/{self._device_id}/detail-or-summary"
        headers = {
            "Authorization": f"Bearer {self._token}",
            "User-Agent": "iqua-water-poller/0.1",
        }

        async with self._session.get(
            self.BASE_URL + DATA_ENDPOINT, headers=headers
        ) as resp:
            resp.raise_for_status()
            return await resp.json()
