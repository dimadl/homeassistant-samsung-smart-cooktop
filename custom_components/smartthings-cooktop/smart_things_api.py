import requests, logging
from requests.exceptions import HTTPError
from .const import SMART_THINGS_API_BASE
from .oauth_smart_thing import OauthSessionSmartThings

_LOGGER = logging.getLogger(__name__)

class Cooktop:
    def __init__(self, device_id, name):
        self._device_id = device_id
        self._name = name

    @property
    def name(self):
        return self._name

    @property
    def device_id(self):
        return self._device_id

class CooktopAPI:
    def __init__(self, oauth_session: OauthSessionSmartThings):
        self.base_url = SMART_THINGS_API_BASE
        self.oauth_session = oauth_session

    def get_cooktops(self) -> list[Cooktop]:
        """Retieves all cooktops from the account."""

        _LOGGER.info("[Request] GET %s/devices", self.base_url)

        header = {'Authorization': f'Bearer {self.oauth_session.get_token()}'}
        response = requests.get(f"{self.base_url}/devices", headers=header, timeout=30)
        response.raise_for_status()

        try:

            _LOGGER.info("[Response] GET %s/devices: %s", self.base_url, response)

            receivedDevices = response.json()["items"]
            return [
                Cooktop(cooktop["deviceId"], f"({cooktop["deviceTypeName"]} {cooktop["name"]})")
                    for cooktop in filter(lambda device: "deviceTypeId" in device and device["deviceTypeId"] == "Cooktop",receivedDevices)

            ]

        except HTTPError as http_err:
            _LOGGER.error("HTTP error occurred: %s", http_err)


    def get_cooktop_burners_status(self, device_id, burner_ids):
        """Retieves the status of cooktop by id."""

        _LOGGER.info("GET %s/devices/%s/status", self.base_url, device_id)

        header = {'Authorization': f'Bearer {self.oauth_session.get_token()}'}
        response = requests.get(f"{self.base_url}/devices/{device_id}/status", headers=header, timeout=30)
        response.raise_for_status()

        try:
            full_details = response.json()
            power = full_details.get("components").get("main").get("switch").get("switch").get("value", "off") == 'on'
            is_locked = full_details.get("components").get("main").get("samsungce.kidsLockControl").get("lockState").get("value", "unlocked") == 'locked'
            burners = {}
            for burner_id in burner_ids:
                burner = full_details.get("components").get(burner_id, {})

                burners[burner_id] = {
                    "level": burner.get("samsungce.cooktopHeatingPower").get("manualLevel").get("value", 0),
                    "taimer": burner.get("samsungce.countDownTimer").get("currentValue").get("value", 0)
                }

            return {
                "power": power,
                "is_locked": is_locked,
                "burners": burners
            }
        
        except HTTPError as http_err:
            _LOGGER.error("HTTP error occurred: %s", http_err)

