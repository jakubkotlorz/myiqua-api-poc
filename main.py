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


BASE_URL = "https://api.myiquaapp.com/v1"

def login(email, password):
    LOGIN_ENDPOINT = "/auth/login"
    url = BASE_URL + LOGIN_ENDPOINT
    payload = {
        "email": email,
        "password": password
    }
    r = requests.post(url, json=payload, timeout=20)
    r.raise_for_status()
    data = r.json()
    return data["access_token"]


def get_data(token, device_id):
    DATA_ENDPOINT = f"/devices/{device_id}/detail-or-summary"
    url = BASE_URL + DATA_ENDPOINT
    headers = {
        "Authorization": f"Bearer {token}",
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
        sys.exit(4)

    token = None
    while True:
        try:
            if token is None:
                token = login(username, password)
                logging.info(f"Logged in, token acquired ({token[:10]}...)")

            data = get_data(token, device_id)

            water_updated = data["device"]["properties"]["gallons_used_today"]["updated_at"]
            water_usage = data["device"]["properties"]["gallons_used_today"]["converted_value"]
            logging.info(f"Water usage: {water_usage}\tUpdated: {water_updated}")

            sleep_time = random.uniform(min_sec, max_sec)

        except requests.exceptions.HTTPError as e:
            status = e.response.status_code
            logging.error(f"HTTP {status}: {e.response.text}")

            if status == 401:
                logging.warning("Token expired, re-authenticating")
                token = None
                continue
            else:
                logging.error(f"HTTP error: {status}, {e}")
                sys.exit(1)

        except requests.exceptions.RequestException as e:
            logging.error(f"Network error: {e}")
            sys.exit(2)

        except KeyError as e:
            logging.error(f"JSON error: {e}")
            sys.exit(3)
        
        time.sleep(sleep_time)


if __name__ == "__main__":
    main()
