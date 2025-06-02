import requests

class CooktopAPI:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.token = token

    def get_cooktop_burners_status(self, device_id, burner_ids):
        header = {'Authorization': 'Bearer {}'.format(self.token)}
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
