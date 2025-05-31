from homeassistant.components.switch import SwitchEntity
from .const import DOMAIN

def setup_platform(hass, config, add_entities, discovery_info=None):
    api = hass.data[DOMAIN]
    add_entities([CooktopPowerSwitch(api)], True)

class CooktopPowerSwitch(SwitchEntity):
    def __init__(self, api):
        self.api = api
        self._is_on = False

    @property
    def name(self):
        return "Cooktop Power"

    @property
    def is_on(self):
        return self._is_on

    def update(self):
        status = self.api.get_cooktop_burners_status("2163cb5b-4ee0-4e1c-b74e-0b4bcdaf2009")
        self._is_on = status.get("components").get("main").get("switch").get("switch").get("value", False) | False