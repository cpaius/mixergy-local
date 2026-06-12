"""Mixergy Local - Config flow."""
from __future__ import annotations
import logging
import aiohttp
import async_timeout
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from homeassistant.data_entry_flow import FlowResult
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
DATA_SCHEMA = vol.Schema({vol.Required(CONF_HOST, default="192.168.33.116"): str})

class MixergyLocalConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        errors = {}
        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            try:
                async with async_timeout.timeout(10):
                    async with aiohttp.ClientSession() as session:
                        async with session.get(f"http://{host}/status") as resp:
                            if resp.status == 200:
                                data = await resp.json(content_type=None)
                                if "charge" in data:
                                    await self.async_set_unique_id(f"mixergy_local_{host}")
                                    self._abort_if_unique_id_configured()
                                    return self.async_create_entry(title=f"Mixergy Tank ({host})", data={CONF_HOST: host})
                                else:
                                    errors["base"] = "invalid_response"
                            else:
                                errors["base"] = "cannot_connect"
            except aiohttp.ClientError:
                errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "unknown"
        return self.async_show_form(step_id="user", data_schema=DATA_SCHEMA, errors=errors)
