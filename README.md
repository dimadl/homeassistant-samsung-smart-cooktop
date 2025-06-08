# SmartThings Cooktop

>[!CAUTION]
>The integration is under development!

The custom integration adds support for SmartThings compatible Cooktops

## Motivation
The idea came from a need to integrate a Samsung cooktop with a hood (not a Samsung one, for example to make it work with hob2hood :). It was supposed to be the integration for Home Assistant are not exposed to publicity.

## Installation

### Using [HACS](https://hacs.xyz/) (recommended)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=dimadl&repository=homeassistant-samsung-smart-cooktop&category=integration)

### Manual installation
1. Download the latest release of `homeassistant-samsung-smart-cooktop` repository. The link - [*samsung-smart-cooktop.zip*](https://github.com/dimadl/homeassistant-samsung-smart-cooktop/releases/latest/download/samsung-smart-cooktop.zip.zip)
2. Copy the `custom_components/samsung-smart-cooktop` folder from the downloaded files and paste the it into your Home Assistant's custom components directory: `<home_assistant_folder>/custom_components/samsung-smart-cooktop`
5. Restart Home Assistant.

## Configuration

### Config flow (recommended)

When the integration is installed using one of the above approach, it should be added to the list of integrations. Follow the steps to do that:
1. Open `Settings` and go to `Devices & services`
2. Click `Add Integration` and search for `Smart Things Cooktop`

You can also use the following [My Home Assistant](http://my.home-assistant.io/) link:

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=cooktop)

#### Config Flow Fields

The first step cover SmartThings OAuth credentials

| Key                   | Type     | Required | Description                                                                                                                  |
|-----------------------|----------|----------|------------------------------------------------------------------------------------------------------------------------------|
| `Client ID`           | `string` | `True`   | Client ID of the registered app. See [Authorization in Smart Things](#authorization-in-smart-things)                         |
| `Client Secret`       | `string` | `True`   | Client Secret of the registered app. See [Authorization in Smart Things](#authorization-in-smart-things)                     |
| `Redirect URL`        | `string` | `True`   | Redirect URL  of the registered app. See [Authorization in Smart Things](#authorization-in-smart-things)                     |
| `Authorization code`  | `string` | `True`   | A code generated at the end of the autorization process. See [Authorization in Smart Things](#authorization-in-smart-things) |

The second step will ask you to choose a cooktop device you'd like to use for this integration

> [!WARNING]
> At this moment the integration works with one cooktop

#### Authorization in Smart Things
At some point Samsung limitted the TTL of Personal Tokens to 24 hours only, which makes it hard to support in the Home Assistant. But there is OAuth flow to the rescue.

1. Install [SmartThings CLI](https://github.com/SmartThingsCommunity/smartthings-cli)
2. Run the following command to create your application in SmartThings: `smartthings apps:create`
3. Choose `OAuth-In App` from the promted list of options
4. You will be guided through the wizard of app creation.
    * App name can be whatever you want
    * Redirect URL: you can put `https://httpbin.org/get`
    * Scopes required for the integration to work: `r:devices:*`, `w:devices:*`, `x:devices:*`
5. When the app is create its details will be shown
```
  Display Name     <you_app_display_name>
  App Id           <your app id>
  App Name         <your_app_name>
  Description      <your_app_discription>
  Single Instance  true
  Classifications  CONNECTED_SERVICE
  App Type         API_ONLY
────────────────────────────────────────────────────────────────


OAuth Info (you will not be able to see the OAuth info again so please save it now!):
───────────────────────────────────────────────────────────
 OAuth Client Id      <you_app_client_id>
 OAuth Client Secret  <you_app_client_secret>
───────────────────────────────────────────────────────────
```

6. Save `<you_app_client_id>`, `<you_app_client_secret>`, and `<your_redirect_url>`. These are important settings of your integration
7. SmartThing OAuth uese Authorization Code flow, therefore the next step is to receive the `code`
8. Build the link for auth. Here is template:
```
https://api.smartthings.com/oauth/authorize?client_id=<you_app_client_id>&response_type=code&redirect_uri=<your_redirect_url>&scope=r:devices:*+w:devices:*+x:devices:*`
```
9. Open the link in a browser
10. Follow the suggest steps to authorize.
11. When authorized, you will be redirect to `<your_redirec_url>` with `code` in the path. For exmaple: `http://<your_redirect_url>?code=<auth_code>`
12. This code is for one time usage

## Exposed entities

All exposed entities are `read_only`. The cooktop API in SmartThings doesn't provide actions.

- Power on/off: `switch.cooktop_power`
- Lock on/off: `switch.cooktop_lock`
- Burner levels: 
  - `number.cooktop_burner_01_level`
  - `number.cooktop_burner_02_level`
  - `number.cooktop_burner_03_level`
  - `number.cooktop_burner_04_level`
- Timers associated with each burner
  - `number.cooktop_burner_01_timer`
  - `number.cooktop_burner_02_timer`
  - `number.cooktop_burner_03_timer`
  - `number.cooktop_burner_04_timer`
- Energy (artificial culculation based on the burners levels)
  - `sensor.cooktop_energy`

## Tested devices

- Samsung NZ64B5046KK 
