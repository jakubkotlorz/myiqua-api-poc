"""myiqua_softenener integration."""

from datetime import timedelta
import asyncio
import logging


_LOGGER = logging.getLogger(__name__)


class PollingCoordinator:
    def __init__(self, api, update_interval: float):
        self.api = api
        self._update_interval = update_interval
        self.data = None
        self._task = None
        self._stopped = False

    async def start(self):
        if self._task:
            return

        _LOGGER.info("Starting PollingCoordinator")
        self._stopped = False
        self._task = asyncio.create_task(self._run())

    async def stop(self):
        _LOGGER.info("Stopping PollingCoordinator")
        self._stopped = True
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _run(self):
        while not self._stopped:
            try:
                self.data = await self.api.get_device_data()
            except Exception as e:
                _LOGGER.error(f"Coordinator error: {e}")
            await asyncio.sleep(self._update_interval)