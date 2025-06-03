import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import UnitOfEnergy
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.restore_state import RestoreEntity

from .const import DOMAIN, BURNERS

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = hass.data[DOMAIN]["coordinator"]
    async_add_entities([
        CooktopEnergySensor(coordinator)
    ])

class CooktopEnergySensor(CoordinatorEntity, SensorEntity, RestoreEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Cooktop Energy"
        self._attr_device_class = SensorDeviceClass.ENERGY
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        self._attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
        self._total = 0.0

    async def async_added_to_hass(self):
        """Restore previous state."""
        await super().async_added_to_hass()
        if (last_state := await self.async_get_last_state()) is not None:
            try:
                self._total = float(last_state.state)
            except (ValueError, TypeError):
                self._total = 0.0

    @property
    def native_value(self):
        burners_data = self.coordinator.data.get("burners", {})

        _LOGGER.debug(f"Get the burner data: {burners_data}")
        for burner_id, burner_info in burners_data.items():
          burner_level = burner_info.get("level", 0)
          if burner_level == 0:
              continue

          _LOGGER.debug(f"Search for the power value for the level: {burner_level}")
          power_map = BURNERS.get(burner_id, {}).get("power_consumption_map", [])
          matching = next((entry for entry in power_map if entry["level"] == burner_level), None)
          if matching:
            found_power = matching.get("power", 0.0)
            self._total += found_power * 10 / 3600000
            _LOGGER.debug(f"Found power of the level: {burner_level}, power: {found_power}")


        _LOGGER.debug(f"Setting new: {self._total}")
        return round(self._total, 3)

    async def async_update(self):
        pass

