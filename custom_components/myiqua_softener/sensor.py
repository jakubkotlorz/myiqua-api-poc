from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN



async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [
            MyIquaWaterUsageSensor(coordinator),
        ]
    )


class MyIquaWaterUsageSensor(SensorEntity):
    _attr_name = "MyIqua Water Usage Today"
    _attr_unit_of_measurement = "gal"

    def __init__(self, coordinator):
        self.coordinator = coordinator

    @property
    def native_value(self):
        try:
            return (
                self.coordinator.data["device"]["properties"]
                ["gallons_used_today"]["converted_value"]
            )
        except (TypeError, KeyError):
            return None

    async def async_update(self):
        await self.coordinator.async_request_refresh()
