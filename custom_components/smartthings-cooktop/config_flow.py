import voluptuous as vol
import logging
import asyncio

from homeassistant import config_entries
from homeassistant.helpers.selector import selector
from homeassistant.helpers.storage import Store
from .const import DOMAIN
from .oauth_smart_thing import OauthSessionContext, OauthCodeFlowCredentials, OauthSessionSmartThings
from .smart_things_api import CooktopAPI, Cooktop

_LOGGER = logging.getLogger(__name__)

class CooktopConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """The configuration flow for Smart Thing Cooktop"""

    def __init__(self) -> None:
        self._client_id = None
        self._client_secret = None
        self._redirect_url = None
        self._cooktops = list[Cooktop]

    async def async_step_user(self, user_input=None):
        """Init config flow when a use is interacting"""

        if user_input is not None:
            _LOGGER.info(f"User input: {user_input}")

        return self.async_show_form(
            step_id="creds",
            data_schema=self.get_schema_creds()
        )


    async def async_step_creds(self, user_input=None):
        """Step 1. Set up Smart Things OAuth credentials and fetch available cooktops"""

        errors = {}
        if user_input is not None:
            self._client_id = "e6a4d874-f230-4730-82be-280f4d4375ef"
            self._client_secret = "5647211c-30d1-4178-829f-17b2aff4e189"
            self._redirect_url = "https://httpbin.org/get"
            code = user_input["code"]

            try:
                _LOGGER.info("Creating OAuth session")

                code_flow_credentials = OauthCodeFlowCredentials(self._client_id, self._client_secret, self._redirect_url, code)
                oauth_context = OauthSessionContext()
                oauth_context.create_session(self.hass, code_flow_credentials)

                _LOGGER.info("OAuth session has been created. Proceeding to the retriaval of cooktops")

                cooktop_api = CooktopAPI(oauth_context.get_session())

                # cooktops: list[Cooktop] = await self.hass.async_add_executor_job(
                #             cooktop_api.async_get_cooktops)

                cooktops: list[Cooktop] = await cooktop_api.async_get_cooktops()

                # loop = asyncio.get_event_loop()
                # cooktops: list[Cooktop] = asyncio.run_coroutine_threadsafe(
                #             cooktop_api.async_get_cooktops(), loop
                # ).result()

                if len(cooktops) > 0:
                    _LOGGER.info(f"Loaded cooktops {cooktops}")
                    self._cooktops = cooktops

                    return await self.async_step_select_cooktop()

            except Exception as e:
                errors = {"cooktops": "Cooktops were not recceived due to an erro"}
                _LOGGER.error(str(e))

        return self.async_show_form(
            step_id="creds",
            data_schema=self.get_schema_creds(),
            errors=errors
        )

    async def async_step_select_cooktop(self, user_input=None):
        """Step 2. Select a cooktop from the list"""

        if user_input is not None:
            device_id = user_input["device_id"]

            """Step 3. Te configuration flow is finished"""

            _LOGGER.info(f"The Smart Thing Cooktop configuration finished. The chosen device id: {device_id}")
            data = {
                "device_id": device_id
            }
            return self.async_create_entry(title="Cooktop", data=data)

        return self.async_show_form(
            step_id="select_cooktop",
            data_schema=self.get_schema_select_cooktop()
        )


    def get_schema_select_cooktop(self, user_input=None):
        """The schema for the selection of a cooktop from the list availble in the Smart Things account"""

        cooktop_options = [{"label": c.name, "value": c.device_id} for c in self._cooktops]
        return vol.Schema({
            vol.Required("device_id"): selector(
                {"select": {"options": cooktop_options}}),
        })


    def get_schema_creds(self, user_input=None):
        """The schema for the credentials of the application registered in Smart Things"""

        return vol.Schema({
            vol.Required("client_id"): str,
            vol.Required("client_secret"): str,
            vol.Required("redirect_url"): str,
            vol.Required("code"): str,
        })
