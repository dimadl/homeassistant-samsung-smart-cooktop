"""The samsung_cooktop integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .const import DOMAIN
from .smart_things_api import CooktopAPI
from .oauth_smart_thing import OauthSessionContext
from .coordinator import CooktopDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

def cooktop_api_init(hass) -> CooktopAPI:
    oauth_context = OauthSessionContext()
    oauth_context.create_session(hass, None)
    cooktop_api = CooktopAPI(oauth_context.get_session())
    return cooktop_api

async def async_setup(hass: HomeAssistant, config: dict):
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    _LOGGER.info("Setup entry flow. Very begnning")
    
    cooktop_api = cooktop_api_init(hass)
    device_id = entry.data["device_id"]

    _LOGGER.info(f"The device with id {device_id} will be mointored by the integration. Setting up the rest")

    coordinator = CooktopDataUpdateCoordinator(hass, cooktop_api, device_id,
                                                ["burner-01", "burner-02", "burner-03", "burner-04"])

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN]["coordinator"] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, ["switch", "number", "sensor"])

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    return await hass.config_entries.async_unload_platforms(entry, ["switch", "number", "sensor"])
