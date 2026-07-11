# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

`havenlighting` is a small Python client library for the Haven Lighting API (controlling landscape/exterior lighting systems via a cloud API). Published to PyPI.

## Commands

```bash
# Install for development (editable, with test deps)
pip install -e ".[dev]"

# Run all tests
pytest

# Run a single test file / test
pytest tests/test_client.py
pytest tests/test_client.py::test_token_refresh

# Run the live demo (requires real credentials)
cp .env.example .env   # fill in HAVEN_EMAIL / HAVEN_PASSWORD
python examples/demo.py
```

There is no lint/type-check/build tooling configured beyond `pytest` and standard `setuptools` packaging (`pyproject.toml`).

## Architecture

Request flow: `HavenClient` → `Credentials` → `curl_cffi` → Haven's 2025 Cloud API (`stg-api.havenlighting.com`).

- **`client.py` (`HavenClient`)** — public entry point. Holds a `Credentials` instance and caches discovered `Location`/`Light` objects. Thin wrapper: `authenticate()` and `discover_locations()` delegate immediately to `Credentials` / `Location.discover()`.
- **`credentials.py` (`Credentials`)** — owns the auth token, refresh token, user id, and a persistent `curl_cffi.requests.Session` (held on the instance, not a fresh connection per call — this library is expected to be polled periodically, e.g. by a Home Assistant integration). It's the only place that makes HTTP calls; all device/location objects hold a reference to the same `Credentials` instance rather than making requests themselves.
  - `make_request()` is the public entry point used by everything except login: it calls `_make_request_internal()`, and on `AuthenticationError` (a 401) transparently calls `refresh_token()` and retries the request once. If refresh fails, it raises.
  - `_make_request_internal()` does the actual HTTP call. Responses are flat JSON (no `{success, data}` envelope) — a non-2xx status raises `ApiError` (via `_extract_error_message`, which pulls `title` and flattens ASP.NET's `errors: {field: [reasons]}` validation-error shape into the message — don't just surface `title` alone, it's often a generic "One or more validation errors occurred." with the actually useful detail in `errors`), 401 raises `AuthenticationError`. `_update_credentials` wraps missing-field `KeyError`s into `ApiError` rather than letting them leak as a raw `KeyError` — treat any direct `data[...]` access on API response bodies with the same suspicion (missing keys are a real, seen failure mode, not hypothetical).
  - **Must use `curl_cffi.requests` with `impersonate="chrome"`, not the stdlib `requests` library.** Empirically verified (2026-07): Haven's Azure Front Door WAF returns a `403 "The request is blocked."` HTML page for `requests`/urllib3's TLS fingerprint specifically — reproduced with byte-for-byte identical headers/UA to the real mobile app, so it is not a header/payload issue. Plain `curl` and `curl_cffi` (and the real app's CFNetwork stack) pass fine from the same IP. If auth calls start 403ing again, suspect the WAF fingerprinting rules changed, not the payload shape.
  - Single API base (`config.py`): `API_BASE = "https://stg-api.havenlighting.com/api"`. Confirmed via live mitmproxy capture of the real iOS app — there is no separate prod/test host split anymore (that was true of the pre-2025 API this library originally targeted).
- **`devices/location.py` / `devices/light.py`** — device models. `Location.discover()` calls `GET /user/GetUserInfo/` to get the account's `defaultLocationId`. **Known limitation: only the default location is discoverable** — the pre-2025 API's `/Location/OrderedLocationV2` returned every location on the account, but `GetUserInfo` only exposes `defaultLocationId`; there's no verified 2025-API equivalent for multi-location accounts yet. `Location.get_lights()` calls `GET /Location/InformationSummaryWithAllZonesGroup/{location_id}` — one endpoint returns lights, zones, groups, capabilities, and the canonical color-id table in a single response — and always refetches (no staleness caching), since it's also how `Light.is_on` gets refreshed. State lives in `models.py` dataclasses (`LocationData`, `LightData`); every mutating action (`Light.turn_on/turn_off`) goes back through the shared `Credentials.make_request` to `POST /Commands/On` or `/Off` with `{"id": light_id, "type": "Light"}`, and checks the `success` field on *every* element of the (list-shaped) response — not just the first, since a future group/multi-light command could return more than one result.
- **No brightness/color/group support** — deliberately out of scope. The account this was built against only has on/off-capable lights (`capabilities.devices` shows `ON_OFF` only), so `set_brightness`/`set_color` were never implemented against a verified request shape. `LightData` still parses `lightBrightnessId`/`colorId`/`patternSpeedId` for read access if the API returns them, but there's no verified way to *write* them yet — don't invent one without a real capture to check against.
- **`config.py`** — all magic numbers/strings (light on/off status codes, default brightness/color/pattern-speed — brightness defaults to `10`, the max of Haven's 0-10 scale, not a 0-100-style value — the API base, `app-haven-source`/`app-haven-version` headers) live here, not inline in `devices/`.
- **`exceptions.py`** — `HavenException` base, with `AuthenticationError`, `ApiError`, `DeviceError` subclasses. Callers generally catch `AuthenticationError` for auth-required-but-missing/expired-token cases and `ApiError` for general request failures.

## Testing conventions

Tests mock at the `Credentials._make_request_internal` or `Credentials.make_request` boundary (see `tests/conftest.py`), never real HTTP. Fixtures build a `Credentials()` object, patch its request method, then attach it to a `HavenClient` via `client._credentials = credentials` before authenticating — this is the standard pattern for constructing an "authenticated" client in tests without hitting the network. `tests/test_light.py` mocks `Credentials` itself (via `mocker.Mock(spec=Credentials)`) to test the on/off command success/failure parsing in isolation.

## Partner repo: `../haven-hass`

`../haven-hass` (github.com/mickeyschwab/haven-hass) is a Home Assistant custom component that wraps this library — it's the reason this library exists as a standalone PyPI package rather than living inline in one project. It pins `havenlighting>=0.1.5` in `custom_components/haven_lighting/manifest.json` and only consumes the public surface exported from `havenlighting/__init__.py` (`HavenClient`, `Light`, `Location`, `AuthenticationError`, etc.), so:

- Any change to `HavenClient.authenticate()` / `discover_locations()`, `Location.get_lights()`, or `Light.turn_on/turn_off()` signatures is a breaking change for `haven-hass` and needs a version bump here plus a corresponding `requirements` bump there.
- HA calls every blocking method (`authenticate`, `discover_locations`, `get_lights`, `turn_on`/`turn_off`) via `hass.async_add_executor_job`, since this library is synchronous (`curl_cffi`-based, no asyncio) — don't assume a caller can `await` these directly.
- `haven-hass/custom_components/haven_lighting/light.py` reaches past the public API into internals: `light._data.brightness` and `location._location_id`. These are private attributes with no stability guarantee — renaming/restructuring `LightData`/`Location` internals silently breaks `haven-hass` even though it's not a "public API" change from this repo's point of view. Check that repo before renaming anything under `devices/` or `models.py`.
- There is a separate, unrelated community fork `hass-haven-lighting-redux` (different maintainer, domain `haven`, no dependency on the `havenlighting` PyPI package) — not a consumer of this library, don't confuse it with `../haven-hass` when checking for breakage.

When making breaking changes here, check `../haven-hass` for usages before finalizing an API, and consider whether both repos need to move together.

The 2025 API rewrite (see Architecture above) swapped the runtime HTTP dependency from `requests` to `curl_cffi` — `haven-hass`'s `manifest.json` pins `havenlighting>=0.1.5` (a floor, not an exact version), so it'll pick up `curl_cffi` transitively on next install without a manifest change, but Home Assistant's own dependency resolution/HACS packaging should be checked once this is released to PyPI, since `curl_cffi` ships compiled wheels rather than being pure-Python like `requests`.
