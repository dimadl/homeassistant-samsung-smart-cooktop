"""The samsung_cooktop integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .smart_things_api import CooktopAPI
from .oauth_smart_thing import OauthSessionContext
from .coordinator import CooktopDataUpdateCoordinator


async def async_setup(hass: HomeAssistant, config: dict):
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    oauth_context = OauthSessionContext()
    api = CooktopAPI(oauth_context.get_session())

    device_id = entry.data["device_id"]
    coordinator = CooktopDataUpdateCoordinator(hass, api, device_id,
                                                ["burner-01", "burner-02", "burner-03", "burner-04"])

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN]["coordinator"] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, ["switch", "number", "sensor"])

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    return await hass.config_entries.async_unload_platforms(entry, ["switch", "number", "sensor"])
