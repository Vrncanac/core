"""Config flow for Axion Lighting integration."""

from __future__ import annotations

from typing import Any

from libaxion_dmx import AxionDmxApi
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_PASSWORD
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import selector

from .const import _LOGGER, CONF_CHANNEL, CONF_LIGHT_TYPE, DOMAIN

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Required(CONF_CHANNEL): vol.All(vol.Coerce(int), vol.Range(min=1)),
        vol.Required(CONF_LIGHT_TYPE): selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=[
                    selector.SelectOptionDict(value="White", label="White"),
                    selector.SelectOptionDict(
                        value="Tunable White", label="Tunable White"
                    ),
                    selector.SelectOptionDict(value="RGB", label="RGB"),
                    selector.SelectOptionDict(value="RGBW", label="RGBW"),
                    selector.SelectOptionDict(value="RGBWW", label="RGBWW"),
                ],
                translation_key="light_type",
                multiple=False,
                mode=selector.SelectSelectorMode.DROPDOWN,
            )
        ),
    }
)


class AxionConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Axion Lighting."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            api = AxionDmxApi(user_input[CONF_HOST], user_input[CONF_PASSWORD])
            # Validate the user input and authenticate
            try:
                if not await api.authenticate():
                    raise InvalidAuth  # noqa: TRY301
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception as e:  # noqa: BLE001
                _LOGGER.exception("Unexpected exception: %s", e)
                errors["base"] = "unknown"
            else:
                # Return the validated entry data
                return self.async_create_entry(
                    title=f"Axion DMX Light - Channel {user_input[CONF_CHANNEL]}",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
