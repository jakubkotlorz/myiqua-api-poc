# MyIqua API – Home Assistant integration & standalone client

This repository contains a reverse-engineered client for the MyIqua cloud API
used by Viessmann smart water softeners, together with a Home Assistant
integration built on top of it.

The project started as a proof-of-concept and API exploration, and is now
evolving into a stable, long-running Home Assistant integration focused on
reliable water usage monitoring.

---

## Project structure

The repository consists of two related but independent parts:

### 1. Home Assistant integration (primary focus)

A native Home Assistant integration implemented using:

- ConfigFlow (UI configuration)
- DataUpdateCoordinator (rate-limited polling)
- Shared aiohttp session
- Proper HA lifecycle handling (setup / unload / reauth ready)

**Configuration is done entirely via the Home Assistant UI.**  
No `.ini` files are used by the integration.

Current focus:
- long-term stability
- API rate-limit safety
- reliable water usage data

Additional sensors and features will be added later.

---

### 2. Standalone client (development & debugging)

A minimal standalone client used for:
- API exploration
- debugging requests and responses
- development outside of Home Assistant

This client **still uses a `.ini` file** and is intentionally kept simple.

---

## Features

### Shared API layer
- JWT authentication
- async HTTP client
- rate-limit friendly design
- structured logging

### Home Assistant integration
- UI-based configuration (ConfigFlow)
- single API request per update interval
- cached data via DataUpdateCoordinator
- clean separation between API, coordinator and entities

---

## Home Assistant setup

1. Copy the `custom_components/myiqua_softener` directory into your
   Home Assistant `custom_components` folder.

2. Restart Home Assistant.

3. Go to **Settings → Devices & Services → Add integration**.

4. Search for **MyIqua Softener** and follow the setup wizard:
   - account email
   - account password
   - device ID

The integration will start polling data automatically using a safe update
interval.

---

## Standalone client setup

1. Log in to https://app.myiquaapp.com using your credentials.

2. Select your device in the web UI.

3. Copy the device ID from the browser URL
   (the value after `/devices/`).

4. Create `config.ini` (for example by copying `config.ini__example`).

5. Fill in:
   - account email
   - account password
   - device ID
   - polling interval

6. Run the client:

```bash
python -m standalone.main
