"""The samsung_cooktop integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, SMART_THINGS_API_BASE, CLIENT_ID, CLIENT_SECRET, CODE, SMART_THINGS_TOKEN_URL, REDIRECT_URL, SCOPES
from .smart_things_api import CooktopAPI
from .oauth_smart_thing import OauthSessionSmartThings
from .coordinator import CooktopDataUpdateCoordinator


async def async_setup(hass: HomeAssistant, config: dict):
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    #TBD: Load the auth details from the config entry
    oauth_session = OauthSessionSmartThings(SMART_THINGS_TOKEN_URL, CLIENT_ID, CLIENT_SECRET,REDIRECT_URL, SCOPES, CODE)
    api = CooktopAPI(SMART_THINGS_API_BASE, oauth_session)
    
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
