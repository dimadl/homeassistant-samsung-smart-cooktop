import requests, base64, datetime, logging, time
from .const import SMART_THINGS_TOKEN_URL, SCOPES

_LOGGER = logging.getLogger(__name__)

class OauthSessionSmartThings():
  def __init__(self, client_id, client_secret, redirect_url, code):
    '''[TBD] Move to a DTO'''
    self.token_url = SMART_THINGS_TOKEN_URL
    self.client_secret = client_secret
    self.client_id= client_id
    self.redirect_url = redirect_url
    self.scopes = SCOPES
    self.code=code

    '''Internal state'''
    self.refresh_token = None
    self.token_cache = AccessTokenCache()
    self.initialized = False

  def init_session(self):
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': f'Basic {base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode("utf-8")}',
    }
    payload = f'grant_type=authorization_code&client_id={self.client_id}&client_secret={self.client_secret}&redirect_uri={self.redirect_url}&scope={self.scopes}&code={self.code}'

    response = requests.post(self.token_url, headers=headers, data=payload)
    if response.status_code == 200:
        response_dict = response.json()

        print("Received initial token")
        _LOGGER.info(f"Received response from initialization: {response_dict}")
        self.token_cache.update_token(response_dict["access_token"], response_dict["expires_in"])
        self.refresh_token = response_dict["refresh_token"]

        self.initialized = True
    else: 
      _LOGGER.error(f"Error while initialization of session: {response.json()}")

  def get_token(self):
    if not self.initialized:
      self.init_session()

    if self.token_cache.get_token() is not None:
      return self.token_cache.get_token()

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': f'Basic {base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode("utf-8")}',
    }
    payload = f'grant_type=refresh_token&client_id={self.client_id}&client_secret={self.client_secret}&refresh_token={self.refresh_token}'

    _LOGGER.info(f"Payload {payload}")
    _LOGGER.info(f"Token url {self.token_url}")
    _LOGGER.info(f"headers {headers}")

    response = requests.post(self.token_url, headers=headers, data=payload)
    if response.status_code == 200:
        response_dict = response.json()

        print(f"Received token: {response_dict}")
        _LOGGER.info(f"Received token: {response_dict}")

        self.token_cache.update_token(response_dict["access_token"], response_dict["expires_in"])
        self.refresh_token = response_dict["refresh_token"]

        return response_dict["access_token"]
        
    else: 
      _LOGGER.error(f"Error while regreshing access token: {response.json()}")
      

class AccessTokenCache:
  def __init__(self):
    self._access_token = None
    self._last_time_updated = None
    self._validity = 10

  def update_token(self, access_token, validity):
    self._access_token = access_token
    self._validity = validity
    self._last_time_updated = datetime.datetime.now()

  def get_token(self):
    if (self._last_time_updated is not None and (datetime.datetime.now() - self._last_time_updated) < datetime.timedelta(seconds=self._validity)) and self._access_token is not None:
      _LOGGER.debug("Cache hit. Loaded token from cache")
      return self._access_token
    
    _LOGGER.debug("Cache miss")
    self._access_token = None


class OauthSessionContextMeta(type):
     _instances = {}

     def __call__(cls, *args, **kwargs):
    
        if cls not in cls._instances:
          instance = super().__call__(*args, **kwargs)
          cls._instances[cls] = instance
        return cls._instances[cls]

class OauthSessionContext(metaclass=OauthSessionContextMeta):
  def __init__(self):
    self._session: OauthSessionSmartThings = None
  
  def create_session(self, client_id, client_secret, redirect_url, code):
    self._session = OauthSessionSmartThings(client_id, client_secret, redirect_url, code)

  def get_session(self) -> OauthSessionSmartThings:
    return self._session