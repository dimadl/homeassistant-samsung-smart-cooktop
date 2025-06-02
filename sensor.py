from homeassistant.components.sensor import SensorEntity
from homeassistant.const import UnitOfEnergy
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.restore_state import RestoreEntity

from .const import DOMAIN, BURNERS

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
        if (last_state := await self.async_get_last_sensor_data()) is not None:
            try:
                self._total = float(last_state.native_value)
            except (ValueError, TypeError):
                self._total = 0.0

    @property
    def native_value(self):
        return round(self._total, 3)

    async def async_update(self):
        # Called by HA if should_poll is True — skip if using coordinator instead
        pass

    async def async_write_coordinator_update(self):
      burners_data = self.coordinator.data.get("burners", {})

      for burner_id, burner_info in burners_data.items():
          burner_level = burner_info.get("level", 0)
          if burner_level == 0:
              continue

          power_map = BURNERS.get(burner_id, {}).get("power_consumption_map", [])
          matching = next((entry for entry in power_map if entry["level"] == burner_level), None)
          if matching:
            self._total += matching.get("power", 0.0) * 10 / 3600000

      self.async_write_ha_state()

    # def update(self):
    #     self._total += 0.05  # Simulate energy increase
    #     self._attr_native_value = round(self._total, 3)
