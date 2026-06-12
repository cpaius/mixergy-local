"""Mixergy Local - Data coordinator."""
from __future__ import annotations
import asyncio
import json
import logging
from datetime import timedelta
import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(seconds=30)
_RECONNECT_DELAYS = (5, 10, 30, 60)


class MixergyLocalCoordinator(DataUpdateCoordinator):
    """Coordinator to fetch data from the Mixergy Pi local API."""

    def __init__(self, hass: HomeAssistant, host: str) -> None:
        super().__init__(hass, _LOGGER, name="Mixergy Local", update_interval=SCAN_INTERVAL)
        self.host = host
        self._base_url = f"http://{host}"

    async def _async_update_data(self) -> dict:
        try:
            async with asyncio.timeout(10):
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{self._base_url}/status") as resp:
                        if resp.status != 200:
                            raise UpdateFailed(f"Bad status {resp.status} from /status")
                        return await resp.json(content_type=None)
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Cannot connect to Mixergy Pi at {self.host}: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Error fetching Mixergy data: {err}") from err


class MixergyMeasurementsCoordinator(DataUpdateCoordinator):
    """Coordinator that consumes the Mixergy Pi streaming measurements endpoint."""

    def __init__(self, hass: HomeAssistant, host: str) -> None:
        super().__init__(hass, _LOGGER, name="Mixergy Measurements", update_interval=None)
        self.host = host
        self._base_url = f"http://{host}"
        self._stream_task: asyncio.Task | None = None
        self._accumulated: dict = {}

    async def async_start_stream(self) -> None:
        self._stream_task = self.hass.async_create_background_task(
            self._stream_loop(), "mixergy_measurements_stream"
        )

    async def async_stop_stream(self) -> None:
        if self._stream_task and not self._stream_task.done():
            self._stream_task.cancel()
            try:
                await self._stream_task
            except asyncio.CancelledError:
                pass
        self._stream_task = None

    async def _stream_loop(self) -> None:
        decoder = json.JSONDecoder()
        delay_idx = 0
        while True:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{self._base_url}/measurements") as resp:
                        delay_idx = 0
                        buf = ""
                        async for chunk in resp.content.iter_chunked(1024):
                            buf += chunk.decode("utf-8", errors="replace")
                            while buf.lstrip():
                                buf = buf.lstrip()
                                try:
                                    obj, idx = decoder.raw_decode(buf)
                                    buf = buf[idx:]
                                    self._accumulated.update(obj)
                                    # Only push to HA on slow messages (~500ms cadence).
                                    # Fast power/frequency messages (100ms) just accumulate.
                                    if "soc" in obj or "dro" in obj:
                                        self.async_set_updated_data(self._accumulated.copy())
                                except json.JSONDecodeError:
                                    break
            except asyncio.CancelledError:
                raise
            except Exception as err:
                delay = _RECONNECT_DELAYS[min(delay_idx, len(_RECONNECT_DELAYS) - 1)]
                _LOGGER.warning("Measurements stream error (%s), reconnect in %ds", err, delay)
                delay_idx += 1
                await asyncio.sleep(delay)

    async def _async_update_data(self) -> dict:
        return self._accumulated.copy()
