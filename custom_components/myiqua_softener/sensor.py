from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN



async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    (coordinator, api) = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [
            MyIquaWaterUsageSensor(coordinator),
        ]
    )


class MyIquaWaterUsageSensor(CoordinatorEntity, SensorEntity):

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "MyIqua Water Usage Today"
        self._attr_unit_of_measurement = "l"


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
