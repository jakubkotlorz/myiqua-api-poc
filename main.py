import requests
import logging
import random
import time
import sys
import configparser


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s\t%(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("water.log", "a", "utf-8")
    ]
)


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
                    logging.warning("Token expired, re-authenticating")
                    self._token = None
                    continue
                else:
                    logging.error(f"HTTP {status}: {e.response.text}")
                    raise
            except requests.exceptions.RequestException as e:
                logging.error(f"Network error: {e}")
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
        logging.info(f"Logged in, token acquired ({self._token[:10]}...)")

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


def load_config(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    required = [
        ("auth", "user"),
        ("auth", "password"),
        ("device", "id"),
    ]        
    for section, key in required:
        if key not in config[section]:
            raise RuntimeError(f"Missing config: {section}-{key}")
    username = config["auth"]["user"]
    password = config["auth"]["password"]
    device_id = config["device"]["id"]
    min_sec = 60 * config.getint("polling", "min_minutes", fallback=10)
    max_sec = 60 * config.getint("polling", "max_minutes", fallback=20)
    if min_sec > max_sec:
        raise ValueError(f"MAX time ({max_sec}) must be greater than MIN time ({min_sec})!")
    return username, password, device_id, min_sec, max_sec


def main():
    try:
        username, password, device_id, min_sec, max_sec = load_config("config.ini")
    except Exception as e:
        logging.error(f"Configuration error: {e}")
        sys.exit(1)

    api = IquaApi(username, password, device_id)
    while True:
        try:
            data = api.get_device_data()
            if data:
                water_updated = data["device"]["properties"]["gallons_used_today"]["updated_at"]
                water_usage = data["device"]["properties"]["gallons_used_today"]["converted_value"]
                logging.info(f"Water usage: {water_usage}\tUpdated: {water_updated}")
        except KeyError as e:
            logging.error(f"JSON error: {e}")
            sys.exit(3)
        except Exception as e:
            logging.error(f"API error: {e}")
            sys.exit(2)

        sleep_time = random.uniform(min_sec, max_sec)
        time.sleep(sleep_time)


if __name__ == "__main__":
    main()
