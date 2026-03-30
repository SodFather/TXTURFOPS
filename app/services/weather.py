import httpx
from ..config import get_settings

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

# WMO weather code to description mapping
WMO_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Foggy", 48: "Rime fog", 51: "Light drizzle", 53: "Moderate drizzle",
    55: "Dense drizzle", 61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow", 80: "Slight showers",
    81: "Moderate showers", 82: "Violent showers", 95: "Thunderstorm",
    96: "Thunderstorm w/ hail", 99: "Thunderstorm w/ heavy hail",
}


async def get_forecast(lat: float = None, lon: float = None, days: int = 7) -> dict | None:
    """Get weather forecast from Open-Meteo for the service area."""
    settings = get_settings()
    lat = lat or settings.service_area_lat
    lon = lon or settings.service_area_lon

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                OPEN_METEO_URL,
                params={
                    "latitude": lat,
                    "longitude": lon,
                    "daily": ",".join([
                        "temperature_2m_max", "temperature_2m_min",
                        "precipitation_probability_max", "precipitation_sum",
                        "wind_speed_10m_max", "weather_code",
                    ]),
                    "current": ",".join([
                        "temperature_2m", "wind_speed_10m", "wind_direction_10m",
                        "relative_humidity_2m", "weather_code",
                    ]),
                    "temperature_unit": "fahrenheit",
                    "wind_speed_unit": "mph",
                    "precipitation_unit": "inch",
                    "timezone": "America/Chicago",
                    "forecast_days": days,
                },
                timeout=10.0,
            )
            if resp.status_code == 200:
                return resp.json()
    except (httpx.RequestError, ValueError):
        pass
    return None


async def get_current_conditions(lat: float = None, lon: float = None) -> dict | None:
    """Get current weather conditions for field work."""
    data = await get_forecast(lat, lon, days=1)
    if not data or "current" not in data:
        return None
    c = data["current"]
    return {
        "temperature_f": c.get("temperature_2m"),
        "wind_speed_mph": c.get("wind_speed_10m"),
        "wind_direction": _deg_to_compass(c.get("wind_direction_10m", 0)),
        "humidity_pct": c.get("relative_humidity_2m"),
        "conditions": WMO_CODES.get(c.get("weather_code", 0), "Unknown"),
    }


def parse_daily_forecast(data: dict) -> list[dict]:
    """Parse Open-Meteo response into a list of daily forecast dicts."""
    if not data or "daily" not in data:
        return []
    d = data["daily"]
    days = []
    for i in range(len(d.get("time", []))):
        rain_prob = d["precipitation_probability_max"][i] or 0
        wind_max = d["wind_speed_10m_max"][i] or 0
        temp_max = d["temperature_2m_max"][i] or 0
        days.append({
            "date": d["time"][i],
            "temp_high": d["temperature_2m_max"][i],
            "temp_low": d["temperature_2m_min"][i],
            "rain_probability": rain_prob,
            "precipitation_in": d["precipitation_sum"][i] or 0,
            "wind_max_mph": wind_max,
            "weather_code": d["weather_code"][i],
            "conditions": WMO_CODES.get(d["weather_code"][i], "Unknown"),
            # Flags for spray work
            "rain_risk": rain_prob > 40,
            "wind_risk": wind_max > 10,
            "heat_risk": temp_max > 95,
            "freeze_risk": (d["temperature_2m_min"][i] or 99) <= 32,
        })
    return days


def _deg_to_compass(deg: float) -> str:
    dirs = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
            "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    return dirs[int((deg + 11.25) / 22.5) % 16]
