import logging
from datetime import timedelta
from aiohttp import ClientResponseError
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import DOMAIN
from .api import IquaApiAsync

_LOGGER = logging.getLogger(__name__)


class MyIquaSoftenerDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, api: IquaApiAsync):
        self.api = api

        super().__init__(
            hass,
            _LOGGER,
            name="MyIqua Softener",
            update_interval=timedelta(minutes=15),
        )

    async def _async_update_data(self):
        try:
            _LOGGER.debug("Fetching data from MyIqua API...")
            return await self.api.get_device_data()

        except ClientResponseError as err:
            if err.status in (401, 403):
                raise ConfigEntryAuthFailed from err

            raise UpdateFailed(
                f"MyIqua API HTTP error {err.status}"
            ) from err

        except Exception as err:
            raise UpdateFailed(f"MyIqua communication error: {err}") from err
