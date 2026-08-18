from typing import Any, ClassVar

import httpx

from backend.app.ai.tools.base import BaseTool, ToolResult


class WeatherTool(BaseTool):
    name = "weather"
    description = "Get the current weather for a latitude and longitude."

    parameters: ClassVar[dict] = {
        "type": "object",
        "properties": {
            "latitude": {
                "type": "number",
                "description": "Latitude of the location.",
            },
            "longitude": {
                "type": "number",
                "description": "Longitude of the location.",
            },
        },
        "required": ["latitude", "longitude"],
    }

    async def execute(self, arguments: dict[str, Any]) -> ToolResult:
        latitude = arguments.get("latitude")
        longitude = arguments.get("longitude")

        if latitude is None or longitude is None:
            return ToolResult(
                tool_call_id="",
                name=self.name,
                content="latitude and longitude are required.",
                is_error=True,
            )

        url = "https://api.open-meteo.com/v1/forecast"

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": (
                "temperature_2m,"
                "relative_humidity_2m,"
                "apparent_temperature,"
                "weather_code,"
                "wind_speed_10m"
            ),
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

            current = data["current"]

            return ToolResult(
                tool_call_id="",
                name=self.name,
                content=(
                    f"Temperature: {current['temperature_2m']}°C\n"
                    f"Feels like: {current['apparent_temperature']}°C\n"
                    f"Humidity: {current['relative_humidity_2m']}%\n"
                    f"Wind speed: {current['wind_speed_10m']} km/h\n"
                    f"Weather code: {current['weather_code']}"
                ),
            )

        except (httpx.HTTPError, KeyError) as exc:
            return ToolResult(
                tool_call_id="",
                name=self.name,
                content=f"Weather lookup failed: {exc}",
                is_error=True,
            )
