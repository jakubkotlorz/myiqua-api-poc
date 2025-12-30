import logging
import requests

_LOGGER = logging.getLogger(__name__)


class IquaApi:
    BASE_URL = "https://api.myiquaapp.com/v1"

    def __init__(self, email: str, passw: str, dev_id: str):
        self._email = email
        self._password = passw
        self._device_id = dev_id
        self._token = None

    def get_device_data(self) -> dict:
        max_attempts = 2
        for attempt in range(max_attempts):
            if self._token is None:
                self._login()
            try:
                return self._fetch_data()
            except requests.exceptions.HTTPError as e:
                status = e.response.status_code
                if status == 401 and attempt < max_attempts-1:
                    _LOGGER.warning("Token expired, re-authenticating")
                    self._token = None
                    continue
                else:
                    _LOGGER.error(f"HTTP {status}: {e.response.text}")
                    raise
            except requests.exceptions.RequestException as e:
                _LOGGER.error(f"Network error: {e}")
                raise

    def _login(self):
        LOGIN_ENDPOINT = "/auth/login"
        payload = {
            "email": self._email,
            "password": self._password,
        }
        r = requests.post(IquaApi.BASE_URL + LOGIN_ENDPOINT, json=payload, timeout=20)
        r.raise_for_status()
        data = r.json()
        self._token = data["access_token"]
        _LOGGER.info(f"Logged in, token acquired ({self._token[:10]}...)")

    def _fetch_data(self) -> dict:
        DATA_ENDPOINT = f"/devices/{self._device_id}/detail-or-summary"
        url = IquaApi.BASE_URL + DATA_ENDPOINT
        headers = {
            "Authorization": f"Bearer {self._token}",
            "User-Agent": "iqua-water-poller/0.1",
        }
        r = requests.get(url, headers=headers, timeout=20)
        # remaining = int(r.headers.get("x-ratelimit-remaining", 0))
        # reset_at = r.headers.get("x-ratelimit-reset")
        r.raise_for_status()
        return r.json()