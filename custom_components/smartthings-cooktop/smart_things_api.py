import requests, logging
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

class Burner:
    def __init__(self, level, timer):
        self._level = level
        self._timer = timer
    
    @property
    def level(self):
        return self._level
    
    @property
    def timer(self):
        return self._timer

class CooktopStatus:
    def __init__(self, power: bool, is_locked: bool, burners: list[Burner]):
        self._power = power
        self._is_locked = is_locked
        self._burners = burners

    @property
    def power(self):
        return self._power
    
    @property
    def is_locked(self):
        return self._is_locked
    
    @property
    def burners(self) -> list[Burner]:
        return self._burners

class CooktopAPI:
    def __init__(self, oauth_session: OauthSessionSmartThings):
        self.base_url = SMART_THINGS_API_BASE
        self.oauth_session = oauth_session

    def get_cooktops(self) -> list[Cooktop]:
        """Retieves all cooktops from the account"""
        _LOGGER.info(f"GET {self.base_url}/devices")

        header = {'Authorization': 'Bearer {}'.format(self.oauth_session.get_token())}
        response = requests.get(f"{self.base_url}/devices", headers=header)

        cooktops = []
        if response.status_code == 200:
            receivedDevices = response.json()["items"]
            if receivedDevices:

                cooktops = [
                    Cooktop(cooktop["deviceId"], f"({cooktop["deviceTypeName"]} {cooktop["name"]})")
                        for cooktop in filter(lambda device: "deviceTypeId" in device and device["deviceTypeId"] == "Cooktop",receivedDevices)
                            
                ]

                return cooktops
            else:
                _LOGGER.error("The list of devices is empty")
            
        else: 
            _LOGGER.error("Couldn't load device")


    def get_cooktop_burners_status(self, device_id, burner_ids) -> CooktopStatus:
        """Retieves the status of cooktop by id"""
        _LOGGER.info(f"GET {self.base_url}/devices/{device_id}/status")

        header = {'Authorization': 'Bearer {}'.format(self.oauth_session.get_token())}
        response = requests.get(f"{self.base_url}/devices/{device_id}/status", headers=header)

        if response.status_code == 200:
            
            full_details = response.json()
            power = full_details.get("components").get("main").get("switch").get("switch").get("value", "off") == 'on'
            is_locked = full_details.get("components").get("main").get("samsungce.kidsLockControl").get("lockState").get("value", "unlocked") == 'locked'
            burners = {}
            for burner_id in burner_ids:
                burner = full_details.get("components").get(burner_id, {})
                level = burner.get("samsungce.cooktopHeatingPower").get("manualLevel").get("value", 0)
                timer = burner.get("samsungce.countDownTimer").get("currentValue").get("value", 0)

                burners[burner_id] = Burner(level, timer)

            return CooktopStatus(power, is_locked, burners)
            
        else:
            _LOGGER.info("Couldn't load the status of cooktop with id")

       
