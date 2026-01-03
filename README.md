## MyIquaApp API – Proof of Concept

Small proof-of-concept for polling water usage data from the Iqua cloud API
used by Viessmann Smart water softeners.

This project was created as:
- an API exploration exercise
- a reference implementation for a future Home Assistant integration

### Features

- JWT authentication
- rate-limit friendly polling
- configuration via `.ini` file
- structured logging (stdout + file)

### Setup

1. Log in to https://app.myiquaapp.com using your credentials.

2. Select your device in the web UI.

3. Copy the device ID from the browser URL  
   (the value after `/devices/`, e.g. `1a1a1a1a-2b2b-3c3c-4d4d-xyxyxyxyxyxy`).

4. Create `config.ini` (for example by copying `config.ini__example`).

5. Fill in:
   - your account email
   - your account password
   - the device ID obtained above

6. Optionally adjust the polling interval  
   (avoid very low values to stay within API rate limits).

### Development

#### Running the standalone client

The standalone client can be run locally for development and debugging
without Home Assistant. From the project root:

```bash
python -m standalone.main
```

#### Running tests

Tests are executed using pytest. From the project root:
```bash
python -m pytest
```


### Notes

This project is intended as a local proof-of-concept and learning reference.

Work in progress Home Assistant integration for MyIqua water softeners. 

Standalone client is kept for development and debugging.

