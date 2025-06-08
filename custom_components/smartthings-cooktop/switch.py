from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = hass.data[DOMAIN]["coordinator"]
    async_add_entities([CooktopPowerSwitch(coordinator), CooktopKidsLockSwitch(coordinator)])

class CooktopPowerSwitch(CoordinatorEntity, SwitchEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)

    @property
    def name(self):
        return "Cooktop Power"

    @property
    def is_on(self):
        return self.coordinator.data["power"]

    @property
    def should_poll(self):
        return False
    
class CooktopKidsLockSwitch(CoordinatorEntity, SwitchEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)

    @property
    def name(self):
        return "Cooktop Lock"
    
    @property
    def is_on(self):
        return self.coordinator.data["is_locked"]

    @property
    def should_poll(self):
        return False