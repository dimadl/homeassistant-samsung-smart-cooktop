from homeassistant.components.number import NumberEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = hass.data[DOMAIN]["coordinator"]
    async_add_entities([CooktopBurnerLevel(coordinator, burner_id) for burner_id in coordinator.burner_ids])
    async_add_entities([CooktopBurnerTaimer(coordinator, burner_id) for burner_id in coordinator.burner_ids])

class CooktopBurnerLevel(CoordinatorEntity, NumberEntity):
    def __init__(self, coordinator, burner_id):
        super().__init__(coordinator)
        self._burner_id = burner_id

    @property
    def name(self):
        return f"cooktop_{self._burner_id}_level"

    @property
    def native_value(self):
        return self.coordinator.data["burners"][self._burner_id]["level"]

    @property
    def native_min_value(self):
        return 0

    @property
    def native_max_value(self):
        return 15

    @property
    def step(self):
        return 1

    @property
    def should_poll(self):
        return False

class CooktopBurnerTaimer(CoordinatorEntity, NumberEntity):
    def __init__(self, coordinator, burner_id):
        super().__init__(coordinator)
        self._burner_id = burner_id

    @property
    def name(self):
        return f"cooktop_{self._burner_id}_timer"

    @property
    def native_value(self):
        return self.coordinator.data["burners"][self._burner_id]["taimer"]

    @property
    def native_min_value(self):
        return 0

    @property
    def native_max_value(self):
        return 15

    @property
    def step(self):
        return 1

    @property
    def should_poll(self):
        return False

