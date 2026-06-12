"""Mixergy Local - Data coordinator."""
from __future__ import annotations
import asyncio
import logging
from datetime import timedelta
import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(seconds=30)

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
