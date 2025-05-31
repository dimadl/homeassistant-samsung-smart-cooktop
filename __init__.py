"""The samsung_cooktop integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, SMART_THINGS_API_BASE, SMART_THINGS_API_TOKEN
from .smart_things_api import CooktopAPI


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up samsung_cooktop from a config entry."""
    hass.data[DOMAIN] = CooktopAPI(SMART_THINGS_API_BASE, SMART_THINGS_API_TOKEN)

    return True
