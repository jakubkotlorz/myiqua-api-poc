import logging

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN
from .coordinator import MyIquaSoftenerDataUpdateCoordinator
from .api import IquaApiAsync

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass, config):
    """Set up via YAML (DEV ONLY)."""

    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": "import"},
            data={
                "email": "TEST",
                "password": "TEST",
                "device_id": "TEST",
            },
        )
    )

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up MyIqua Softener from a config entry."""

    session = hass.helpers.aiohttp_client.async_get_clientsession(hass)

    api = IquaApiAsync(
        session=session,
        email=entry.data["email"],
        password=entry.data["password"],
        device_id=entry.data["device_id"],
    )

    coordinator = MyIquaSoftenerDataUpdateCoordinator(hass, api)

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    _LOGGER.info("MyIqua Softener integration set up successfully")

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload MyIqua Softener config entry."""

    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
