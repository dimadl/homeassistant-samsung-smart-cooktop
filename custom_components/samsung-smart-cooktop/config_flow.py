import voluptuous as vol

from homeassistant import config_entries
from .const import DOMAIN

class CooktopConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="Cooktop", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required("device_id"): str}),
        )