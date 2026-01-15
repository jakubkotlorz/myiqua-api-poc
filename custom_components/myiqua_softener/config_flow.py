import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .const import DOMAIN


class MyIquaSoftenerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(
                title="MyIqua Softener",
                data=user_input,
            )

        schema = vol.Schema(
            {
                vol.Required("email"): str,
                vol.Required("password"): str,
                vol.Required("device_id"): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
        )
