import requests

class CooktopAPI:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.token = token

    def get_cooktop_burners_status(self, device_id):
        header = {'Authorization': 'Bearer {}'.format(self.token)}
        response = requests.get(f"{self.base_url}/devices/{device_id}/status", headers=header)
        response.raise_for_status()
        return response.json()