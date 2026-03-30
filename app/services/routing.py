import httpx

OSRM_BASE = "https://router.project-osrm.org"


async def optimize_route(stops: list[dict]) -> dict | None:
    """Optimize a route given a list of stops with lat/lon.

    Each stop: {"id": ..., "lat": float, "lon": float, "name": str}
    Returns optimized order, total distance, total duration, and geometry.
    """
    if len(stops) < 2:
        return {"stops": stops, "total_miles": 0, "total_minutes": 0, "geometry": None}

    coords = ";".join(f"{s['lon']},{s['lat']}" for s in stops)
    url = f"{OSRM_BASE}/trip/v1/driving/{coords}"

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                url,
                params={
                    "overview": "full",
                    "geometries": "geojson",
                    "roundtrip": "false",
                    "source": "first",
                    "destination": "last",
                    "steps": "false",
                },
                timeout=15.0,
            )
            if resp.status_code != 200:
                return None

            data = resp.json()
            if data.get("code") != "Ok":
                return None

            trip = data["trips"][0]
            waypoint_order = [w["waypoint_index"] for w in data["waypoints"]]
            ordered_stops = [stops[i] for i in waypoint_order]

            return {
                "stops": ordered_stops,
                "total_miles": round(trip["distance"] * 0.000621371, 1),
                "total_minutes": round(trip["duration"] / 60, 0),
                "geometry": trip["geometry"],
            }
    except (httpx.RequestError, ValueError, KeyError, IndexError):
        pass
    return None


async def get_drive_time(origin: dict, destination: dict) -> dict | None:
    """Get drive time and distance between two points."""
    coords = f"{origin['lon']},{origin['lat']};{destination['lon']},{destination['lat']}"
    url = f"{OSRM_BASE}/route/v1/driving/{coords}"

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, params={"overview": "false"}, timeout=10.0)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("code") == "Ok":
                    route = data["routes"][0]
                    return {
                        "miles": round(route["distance"] * 0.000621371, 1),
                        "minutes": round(route["duration"] / 60, 0),
                    }
    except (httpx.RequestError, ValueError, KeyError):
        pass
    return None
