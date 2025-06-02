"""The samsung_cooktop integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, SMART_THINGS_API_BASE, SMART_THINGS_API_TOKEN
from .smart_things_api import CooktopAPI
from .coordinator import CooktopDataUpdateCoordinator


async def async_setup(hass: HomeAssistant, config: dict):
    return True  # Nothing needed for now


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    api = CooktopAPI(SMART_THINGS_API_BASE, SMART_THINGS_API_TOKEN)

    coordinator = CooktopDataUpdateCoordinator(hass, api, "deviceID",
                                                ["burner-01", "burner-02", "burner-03", "burner-04"])

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN]["coordinator"] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, ["switch", "number", "sensor"])

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    return await hass.config_entries.async_unload_platforms(entry, ["switch", "number", "sensor"])
