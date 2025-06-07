import requests, logging
from .const import SMART_THINGS_API_BASE

_LOGGER = logging.getLogger(__name__)

class CooktopAPI:
    def __init__(self, oauth_session):
        self.base_url = SMART_THINGS_API_BASE
        self.oauth_session = oauth_session

    def get_cooktops(self):
        header = {'Authorization': 'Bearer {}'.format(self.oauth_session.get_token())}
        response = requests.get(f"{self.base_url}/devices", headers=header)

        cooktops = []
        if response.status_code == 200:
            cooktops = [{"device_id": cooktop["deviceId"], "name": f"({cooktop["deviceTypeName"]} {cooktop["name"]})"} for cooktop in filter(lambda device: "deviceTypeId" in device and device["deviceTypeId"] == "Cooktop", response.json()["items"])]
            
        else: 
            _LOGGER.error("Couldn't load device")

        return cooktops


    def get_cooktop_burners_status(self, device_id, burner_ids):
        _LOGGER.info(f"GET {self.base_url}/devices/{device_id}/status")

        header = {'Authorization': 'Bearer {}'.format(self.oauth_session.get_token())}
        response = requests.get(f"{self.base_url}/devices/{device_id}/status", headers=header)
        response.raise_for_status()
        full_details = response.json()

        power = full_details.get("components").get("main").get("switch").get("switch").get("value", "off") == 'on'
        burners = {}
        for burner_id in burner_ids:
            burner = full_details.get("components").get(burner_id, {})

            burners[burner_id] = {
                "level": burner.get("samsungce.cooktopHeatingPower").get("manualLevel").get("value", 0),
                "taimer": burner.get("samsungce.countDownTimer").get("currentValue").get("value", 0)
            }

        is_locked = full_details.get("components").get("main").get("samsungce.kidsLockControl").get("lockState").get("value", "unlocked") == 'locked'

        return {
            "power": power,
            "is_locked": is_locked,
            "burners": burners
        }
