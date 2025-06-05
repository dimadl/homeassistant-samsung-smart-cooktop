import requests, logging

_LOGGER = logging.getLogger(__name__)

class CooktopAPI:
    def __init__(self, base_url, oauth_session):
        self.base_url = base_url
        self.oauth_session = oauth_session

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
