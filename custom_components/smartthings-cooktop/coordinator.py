from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .smart_things_api import CooktopAPI
import logging

_LOGGER = logging.getLogger(__name__)

class CooktopDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, cooktop_api: CooktopAPI, device_id, burner_ids):
        super().__init__(
            hass,
            _LOGGER,
            name="Cooktop Coordinator",
            update_interval=timedelta(seconds=7),
        )
        self._cooktop_api = cooktop_api
        self._device_id = device_id
        self._burner_ids = burner_ids

    @property
    def burner_ids(self):
        return self._burner_ids

    async def _async_update_data(self):
        _LOGGER.info("Running the job to retrieve the cooktop details")
        return await self._cooktop_api.async_get_cooktop_burners_status(self._device_id, self._burner_ids)
