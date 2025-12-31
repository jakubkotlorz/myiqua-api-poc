import aiohttp
import asyncio
import configparser
import logging
import random
import sys
from iqua_api import IquaApi


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s\t%(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("water.log", "a", "utf-8")
    ]
)


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


async def main():
    try:
        username, password, device_id, min_sec, max_sec = load_config("config.ini")
    except Exception as e:
        logging.error(f"Configuration error: {e}")
        sys.exit(1)

    async with aiohttp.ClientSession() as session:
        api = IquaApi(session, username, password, device_id)
        while True:
            try:
                data = await api.get_device_data()
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
            await asyncio.sleep(sleep_time)


if __name__ == "__main__":
    asyncio.run(main())
