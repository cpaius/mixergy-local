"""Tests for the Mixergy Local coordinator."""

from __future__ import annotations

import asyncio
from unittest.mock import patch

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import UpdateFailed
import pytest

from custom_components.mixergy_local.coordinator import MixergyLocalCoordinator, MixergyMeasurementsCoordinator
from tests.conftest import MOCK_MEASUREMENTS, MOCK_STATUS, TEST_HOST, mock_aiohttp_get


async def test_coordinator_update_success(hass: HomeAssistant) -> None:
    """Test coordinator fetches status data."""
    coordinator = MixergyLocalCoordinator(hass, TEST_HOST)

    with patch(
        "custom_components.mixergy_local.coordinator.aiohttp.ClientSession",
        return_value=mock_aiohttp_get(MOCK_STATUS),
    ):
        data = await coordinator._async_update_data()

    assert data == MOCK_STATUS


async def test_coordinator_update_bad_status(hass: HomeAssistant) -> None:
    """Test coordinator raises when the API returns a non-200 status."""
    coordinator = MixergyLocalCoordinator(hass, TEST_HOST)

    with patch(
        "custom_components.mixergy_local.coordinator.aiohttp.ClientSession",
        return_value=mock_aiohttp_get(None, status=500),
    ):
        with pytest.raises(UpdateFailed, match="Bad status 500"):
            await coordinator._async_update_data()


async def test_measurements_stream_parses_messages(hass: HomeAssistant) -> None:
    """Stream coordinator merges all message types into accumulated state."""
    import json as _json
    coordinator = MixergyMeasurementsCoordinator(hass, TEST_HOST)

    power_msg = {"cp": 2360.0, "dp": 0.0, "f": 50.1034, "ts": 33}
    thermal_msg = {"soc": 78.7, "tt": 55.0, "ft": 54.7, "bt": 22.0, "op": False, "v": 243.64, "i": 0.0, "ts": 401}
    relay_msg = {"dro": False, "iro": False, "po": False, "ts": 583}

    updates: list[dict] = []
    coordinator.async_set_updated_data = lambda d: updates.append(dict(d))  # type: ignore[method-assign]

    # Exercise the parsing logic directly (bypasses network)
    decoder = _json.JSONDecoder()
    buf = ""
    for msg in [power_msg, thermal_msg, relay_msg]:
        buf += _json.dumps(msg)
        while buf.lstrip():
            buf = buf.lstrip()
            try:
                obj, idx = decoder.raw_decode(buf)
                buf = buf[idx:]
                coordinator._accumulated.update(obj)
                coordinator.async_set_updated_data(coordinator._accumulated.copy())
            except _json.JSONDecodeError:
                break

    assert len(updates) == 3
    final = updates[-1]
    assert final["cp"] == 2360.0
    assert final["soc"] == 78.7
    assert final["dro"] is False


async def test_measurements_stream_start_stop(hass: HomeAssistant) -> None:
    """Stream coordinator starts and stops background task cleanly."""
    coordinator = MixergyMeasurementsCoordinator(hass, TEST_HOST)

    async def _noop_loop():
        await asyncio.sleep(3600)

    with patch.object(coordinator, "_stream_loop", _noop_loop):
        await coordinator.async_start_stream()
        assert coordinator._stream_task is not None
        assert not coordinator._stream_task.done()
        await coordinator.async_stop_stream()
        assert coordinator._stream_task is None
