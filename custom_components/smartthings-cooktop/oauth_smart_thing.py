import requests, base64, datetime, logging, asyncio
from requests.exceptions import HTTPError
from .const import SMART_THINGS_TOKEN_URL, SCOPES
from homeassistant.helpers.storage import Store
from homeassistant.core import HomeAssistant
import aiohttp

_LOGGER = logging.getLogger(__name__)

class OauthCodeFlowCredentials:
  def __init__(self, client_id, client_secret, redirect_url, code):
    self._client_secret = client_secret
    self._client_id= client_id
    self._redirect_url = redirect_url
    self._code=code

  @property
  def client_secret(self):
    return self._client_secret

  @property
  def client_id(self):
    return self._client_id

  @property
  def redirect_url(self):
    return self._redirect_url

  @property
  def code(self):
    return self._code

class OauthSessionSmartThings():
  def __init__(self, hass: HomeAssistant, code_flow_credentials: OauthCodeFlowCredentials):
    '''[TBD] Move to a DTO'''
    self._token_url = SMART_THINGS_TOKEN_URL
    self._code_flow_credentials = code_flow_credentials
    self._scopes = SCOPES
    self._store = Store(hass, 1, "oauth_smartthings")

    '''Internal state'''
    self._refresh_token = None
    self._token_cache = AccessTokenCache()
    self._initialized = False

  async def init_session(self):
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': f'Basic {base64.b64encode(f"{self._code_flow_credentials.client_id}:{self._code_flow_credentials.client_secret}".encode()).decode("utf-8")}',
    }
    payload = f'grant_type=authorization_code&client_id={self._code_flow_credentials.client_id}&client_secret={self._code_flow_credentials.client_secret}&redirect_uri={self._code_flow_credentials.redirect_url}&scope={self._scopes}&code={self._code_flow_credentials.code}'

    async with aiohttp.ClientSession() as session:
      async with session.post(self._token_url, headers=headers, data=payload) as resp:
            response_dict = await resp.json()
            _LOGGER.info(f"Received response from initialization: {response_dict}")
            self._token_cache.update_token(response_dict["access_token"], response_dict["expires_in"])
            self._refresh_token = response_dict["refresh_token"]
            await self._store.async_save({
              "refresh_token": self._refresh_token,
              "client_id": self._code_flow_credentials.client_id,
              "client_secret": self._code_flow_credentials.client_secret
            })


  async def get_token(self):

    if not self._refresh_token:
      _LOGGER.debug("No saved refresh token. Trying to load from the store")

      saved_data = await self._store.async_load() or {}
      saved_refresh_token = saved_data.get("refresh_token")
      saved_client_id = saved_data.get("client_id")
      saved_client_secret = saved_data.get("client_secret")

      if saved_refresh_token and saved_client_secret and saved_client_id:
        _LOGGER.debug("Refresh token loaded from the persistant store: %s", saved_refresh_token)
        self._refresh_token = saved_refresh_token
        self._code_flow_credentials = OauthCodeFlowCredentials(saved_client_id, saved_client_secret, None, None)
      else:
        _LOGGER.debug("There is no refresh token in the persistant store. Initializing a session")
        await self.init_session()
        _LOGGER.debug("The session has been initialized. Refresh token %s has been saved in the persistant store")


    if self._token_cache.get_token() is not None:
      _LOGGER.debug("Access token is present in the cache. Returning the cached value")
      return self._token_cache.get_token()

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': f'Basic {base64.b64encode(f"{self._code_flow_credentials.client_id}:{self._code_flow_credentials.client_secret}".encode()).decode("utf-8")}',
    }
    payload = f'grant_type=refresh_token&client_id={self._code_flow_credentials.client_id}&client_secret={self._code_flow_credentials.client_secret}&refresh_token={self._refresh_token}'

    _LOGGER.info(f"Payload {payload}")
    _LOGGER.info(f"Token url {self._token_url}")
    _LOGGER.info(f"headers {headers}")


    async with aiohttp.ClientSession() as session:
      async with session.post(self._token_url, headers=headers, data=payload) as resp:
            response_dict = await resp.json()
            _LOGGER.info(f"Received token: {response_dict}")

            self._token_cache.update_token(response_dict["access_token"], response_dict["expires_in"])
            self._refresh_token = response_dict["refresh_token"]
            await self._store.async_save({
              "refresh_token": self._refresh_token,
              "client_id": self._code_flow_credentials.client_id,
              "client_secret": self._code_flow_credentials.client_secret
            })

            return response_dict["access_token"]

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

  def create_session(self, hass: HomeAssistant, code_flow_credentials: OauthCodeFlowCredentials):
    self._session = OauthSessionSmartThings(hass, code_flow_credentials)

  def get_session(self) -> OauthSessionSmartThings:
    return self._session
