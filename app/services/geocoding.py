import re
import httpx
from ..config import get_settings

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

# Zip-code-to-zone mapping for the TX TURF PROS service area
ZIP_TO_ZONE = {
    "78734": "Lakeway",
    "78738": "Lakeway",
    "78669": "Spicewood",
    "78732": "Lakeway",
    "78733": "Bee Caves",
}


async def geocode_address(address: str) -> dict | None:
    """Geocode an address using Nominatim (free, no API key).

    Returns dict with latitude, longitude, display_name, postcode
    or None on failure. Respects Nominatim rate limits.
    """
    settings = get_settings()
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                NOMINATIM_URL,
                params={
                    "q": address,
                    "format": "json",
                    "limit": 1,
                    "addressdetails": 1,
                    "countrycodes": "us",
                },
                headers={"User-Agent": settings.nominatim_user_agent},
                timeout=10.0,
            )
            if resp.status_code == 200 and resp.json():
                data = resp.json()[0]
                addr_details = data.get("address", {})
                return {
                    "latitude": float(data["lat"]),
                    "longitude": float(data["lon"]),
                    "display_name": data.get("display_name", ""),
                    "postcode": addr_details.get("postcode", ""),
                }
    except (httpx.RequestError, ValueError, KeyError):
        pass
    return None


def assign_zone(address: str = "", zip_code: str = "") -> str | None:
    """Determine the service zone from a zip code or address string."""
    # Try zip code first
    if zip_code:
        zone = ZIP_TO_ZONE.get(zip_code[:5])
        if zone:
            return zone

    # Extract known zip from address text
    match = re.search(r"\b(78734|78738|78669|78732|78733)\b", address)
    if match:
        return ZIP_TO_ZONE.get(match.group(1))

    # Fall back to city name matching
    addr_lower = address.lower()
    if "lakeway" in addr_lower:
        return "Lakeway"
    if "spicewood" in addr_lower:
        return "Spicewood"
    if "bee cave" in addr_lower:
        return "Bee Caves"

    return None
