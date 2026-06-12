"""Tests for the Mixergy Local config flow."""

from __future__ import annotations

from unittest.mock import patch

from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.mixergy_local.const import DOMAIN
from tests.conftest import MOCK_STATUS, TEST_HOST, mock_aiohttp_get


async def test_user_form(hass: HomeAssistant, enable_custom_integrations) -> None:
    """Test the config flow shows the initial form."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"


async def test_user_step_success(hass: HomeAssistant, enable_custom_integrations) -> None:
    """Test a successful config flow."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )

    with patch(
        "custom_components.mixergy_local.config_flow.aiohttp.ClientSession",
        return_value=mock_aiohttp_get(MOCK_STATUS),
    ), patch(
        "custom_components.mixergy_local.coordinator.MixergyMeasurementsCoordinator.async_start_stream",
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input={CONF_HOST: TEST_HOST},
        )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == f"Mixergy Tank ({TEST_HOST})"
    assert result["data"] == {CONF_HOST: TEST_HOST}


async def test_user_step_cannot_connect(
    hass: HomeAssistant, enable_custom_integrations
) -> None:
    """Test config flow when the tank is unreachable."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )

    with patch(
        "custom_components.mixergy_local.config_flow.aiohttp.ClientSession",
        return_value=mock_aiohttp_get(None, status=503),
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input={CONF_HOST: TEST_HOST},
        )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}


async def test_user_step_invalid_response(
    hass: HomeAssistant, enable_custom_integrations
) -> None:
    """Test config flow when the API response is missing expected fields."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )

    with patch(
        "custom_components.mixergy_local.config_flow.aiohttp.ClientSession",
        return_value=mock_aiohttp_get({"state": {}}),
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input={CONF_HOST: TEST_HOST},
        )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_response"}


async def test_user_step_already_configured(
    hass: HomeAssistant, enable_custom_integrations, mock_config_entry
) -> None:
    """Test config flow aborts when the tank is already configured."""
    mock_config_entry.add_to_hass(hass)

    with patch(
        "custom_components.mixergy_local.coordinator.aiohttp.ClientSession",
        return_value=mock_aiohttp_get(MOCK_STATUS),
    ), patch(
        "custom_components.mixergy_local.coordinator.MixergyMeasurementsCoordinator.async_start_stream",
    ):
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )

    with patch(
        "custom_components.mixergy_local.config_flow.aiohttp.ClientSession",
        return_value=mock_aiohttp_get(MOCK_STATUS),
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input={CONF_HOST: TEST_HOST},
        )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"
