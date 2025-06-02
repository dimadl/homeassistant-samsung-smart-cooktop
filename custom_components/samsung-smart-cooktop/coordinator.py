from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
import logging

_LOGGER = logging.getLogger(__name__)

class CooktopDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, api, device_id, burner_ids):
        super().__init__(
            hass,
            _LOGGER,
            name="Cooktop Coordinator",
            update_interval=timedelta(seconds=7),
        )
        self.api = api
        self.device_id = device_id
        self.burner_ids = burner_ids

    async def _async_update_data(self):
        _LOGGER.info("Running the job to retrieve the cooktop details")
        return await self.hass.async_add_executor_job(self.api.get_cooktop_burners_status, self.device_id, self.burner_ids)
