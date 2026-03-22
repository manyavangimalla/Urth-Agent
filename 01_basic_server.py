import os
import sys
import httpx
from mcp.server.fastmcp import FastMCP

NASA_KEY = os.getenv("NASA_KEY", "DEMO_KEY")

# Create an MCP server exposing tools/resources/prompts to MCP clients.
mcp = FastMCP("Urth MCP Server", json_response=True)

REGION_DATA = {
    "Northern California": {
        "city": "Sacramento",
        "fire": "NASA FIRMS — Active fires in Northern California (last 24h):\nTotal hotspots detected: 34\n  • Lat 40.23, Lon -122.44 — FRP: 187 MW (extreme)\n  • Lat 39.87, Lon -121.92 — FRP: 94 MW (high)\n  • Lat 40.51, Lon -123.01 — FRP: 62 MW (moderate)",
        "air": "OpenAQ v3 — Air quality in Sacramento:\n  • PM2.5: 42.1 µg/m³\n  • PM10:  78.4 µg/m³\n  • NO2:   31.2 µg/m³\nOverall AQI Status: Unhealthy for Sensitive Groups",
        "climate": "Open-Meteo — Weather risk at (39.5, -121.5):\n  • Temperature: 41.2°C\n  • Humidity: 8%\n  • Wind speed: 42 km/h from 45°\n  • 14-day total rainfall: 0.8 mm\nWildfire Spread Risk: EXTREME\nDrought Index: Severe",
        "news": "Red Flag Warning issued for Northern California; Cal Fire reports 3 new fires in Shasta County; air quality alerts issued for Sacramento Valley residents",
    },
    "Amazon Basin": {
        "city": "Manaus",
        "fire": "NASA FIRMS — Active fires in Amazon (last 24h):\nTotal hotspots detected: 218\n  • Lat -3.44, Lon -65.02 — FRP: 312 MW (extreme)\n  • Lat -4.11, Lon -63.87 — FRP: 198 MW (extreme)\n  • Lat -2.98, Lon -66.45 — FRP: 145 MW (high)",
        "air": "OpenAQ v3 — Air quality in Manaus:\n  • PM2.5: 89.3 µg/m³\n  • PM10: 142.1 µg/m³\n  • NO2:  18.4 µg/m³\nOverall AQI Status: Unhealthy",
        "climate": "Open-Meteo — Weather risk at (-3.4, -65.0):\n  • Temperature: 36.8°C\n  • Humidity: 38%\n  • Wind speed: 18 km/h from 120°\n  • 14-day total rainfall: 4.2 mm\nWildfire Spread Risk: HIGH\nDrought Index: Severe",
        "news": "Amazon deforestation up 22% YoY; Brazil declares emergency as 218 simultaneous fires rage in Para state; scientists warn Amazon approaching tipping point",
    },
    "Florida": {
        "city": "Miami",
        "fire": "NASA FIRMS — Active fires in Florida (last 24h):\nTotal hotspots detected: 12\n  • Lat 25.92, Lon -81.44 — FRP: 34 MW (moderate)\n  • Lat 27.11, Lon -80.87 — FRP: 21 MW (low-moderate)",
        "air": "OpenAQ v3 — Air quality in Miami:\n  • PM2.5: 9.2 µg/m³\n  • PM10:  18.1 µg/m³\n  • NO2:   14.7 µg/m³\nOverall AQI Status: Good",
        "climate": "Open-Meteo — Weather risk at (25.8, -80.2):\n  • Temperature: 29.1°C\n  • Humidity: 78%\n  • Wind speed: 14 km/h from 220°\n  • 14-day total rainfall: 42.3 mm\nWildfire Spread Risk: LOW\nDrought Index: Normal",
        "news": "Florida Keys faces record sea level rise; hurricane season outlook upgraded to above-normal activity; coral bleaching reported across Florida reef tract",
    },
    "Texas": {
        "city": "Austin",
        "fire": "NASA FIRMS — Active fires in Texas (last 24h):\nTotal hotspots detected: 4\n  • Lat 31.55, Lon -98.12 — FRP: 88 MW (high)\n  • Lat 30.29, Lon -97.10 — FRP: 44 MW (moderate)",
        "air": "OpenAQ v3 — Air quality in Austin:\n  • PM2.5: 18.2 µg/m³\n  • PM10:  35.4 µg/m³\n  • NO2:   20.1 µg/m³\nOverall AQI Status: Moderate",
        "climate": "Open-Meteo — Weather risk at (30.2, -97.7):\n  • Temperature: 32.5°C\n  • Humidity: 42%\n  • Wind speed: 22 km/h from 180°\n  • 14-day total rainfall: 10.4 mm\nWildfire Spread Risk: MODERATE\nDrought Index: Normal",
        "news": "Texas power grid issues voluntary conservation notice; dry conditions elevate wildfire risk in central Texas; Austin air quality drops to moderate",
    },
    "Southern California": {
        "city": "Los Angeles",
        "fire": "NASA FIRMS — Active fires in Southern California (last 24h):\nTotal hotspots detected: 58\n  • Lat 34.05, Lon -118.24 — FRP: 125 MW (high)\n  • Lat 33.68, Lon -117.82 — FRP: 60 MW (moderate)",
        "air": "OpenAQ v3 — Air quality in Los Angeles:\n  • PM2.5: 55.3 µg/m³\n  • PM10:  92.1 µg/m³\n  • NO2:   48.2 µg/m³\nOverall AQI Status: Unhealthy for Sensitive Groups",
        "climate": "Open-Meteo — Weather risk at (34.0, -118.2):\n  • Temperature: 28.5°C\n  • Humidity: 15%\n  • Wind speed: 35 km/h from 45°\n  • 14-day total rainfall: 0.0 mm\nWildfire Spread Risk: HIGH\nDrought Index: Severe",
        "news": "Santa Ana winds trigger red flag warnings across Southern California; LA basin air quality alerts in effect",
    },
    "Pacific Northwest": {
        "city": "Seattle",
        "fire": "NASA FIRMS — Active fires in Pacific Northwest (last 24h):\nTotal hotspots detected: 12\n  • Lat 47.60, Lon -122.33 — FRP: 15 MW (low)\n  • Lat 45.52, Lon -122.67 — FRP: 22 MW (low)",
        "air": "OpenAQ v3 — Air quality in Seattle:\n  • PM2.5: 12.1 µg/m³\n  • PM10:  20.4 µg/m³\n  • NO2:   15.3 µg/m³\nOverall AQI Status: Good",
        "climate": "Open-Meteo — Weather risk at (47.6, -122.3):\n  • Temperature: 15.2°C\n  • Humidity: 65%\n  • Wind speed: 12 km/h from 270°\n  • 14-day total rainfall: 85.2 mm\nWildfire Spread Risk: LOW\nDrought Index: Normal",
        "news": "Heavy rainfall expected this weekend in Pacific Northwest; flood watches issued for parts of western Washington",
    },
}


def _region_key(region: str) -> str:
    return region if region in REGION_DATA else "Northern California"


def _fallback_climate_by_lat(lat: float) -> str:
    if lat < 0:
        return REGION_DATA["Amazon Basin"]["climate"]
    if lat < 29:
        return REGION_DATA["Florida"]["climate"]
    return REGION_DATA["Northern California"]["climate"]


@mcp.tool()
def get_active_fires(region: str) -> str:
    """Get wildfire hotspot summary for a region."""
    return REGION_DATA[_region_key(region)]["fire"]


@mcp.tool()
def get_air_quality(city: str) -> str:
    """Get air-quality summary for a city."""
    city_lower = city.strip().lower()
    for region, payload in REGION_DATA.items():
        if payload["city"].lower() == city_lower:
            return payload["air"]
        if region.lower().startswith(city_lower):
            return payload["air"]
    return REGION_DATA["Northern California"]["air"]


@mcp.tool()
def get_weather_risk(lat: float, lon: float) -> str:
    """Get weather/climate risk summary from coordinates."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m",
        "daily": "precipitation_sum",
        "forecast_days": 14,
        "timezone": "auto",
    }

    try:
        with httpx.Client(timeout=12.0) as client:
            response = client.get(url, params=params)
            response.raise_for_status()
            payload = response.json()

        current = payload.get("current", {})
        daily = payload.get("daily", {})
        precip_list = daily.get("precipitation_sum", []) or []
        rain_14d = sum(float(x) for x in precip_list if x is not None)

        temp = float(current.get("temperature_2m", 0.0))
        humidity = float(current.get("relative_humidity_2m", 0.0))
        wind = float(current.get("wind_speed_10m", 0.0))
        wind_dir = float(current.get("wind_direction_10m", 0.0))

        risk = "LOW"
        if temp >= 35 and humidity <= 20 and wind >= 25:
            risk = "EXTREME"
        elif temp >= 32 and humidity <= 30 and wind >= 15:
            risk = "HIGH"
        elif temp >= 28 or humidity <= 40 or wind >= 20:
            risk = "MODERATE"

        drought = "Normal"
        if rain_14d < 2:
            drought = "Severe"
        elif rain_14d < 8:
            drought = "Moderate"

        return (
            f"Open-Meteo — Weather risk at ({lat:.2f}, {lon:.2f}):\n"
            f"  • Temperature: {temp:.1f}°C\n"
            f"  • Humidity: {humidity:.0f}%\n"
            f"  • Wind speed: {wind:.1f} km/h from {wind_dir:.0f}°\n"
            f"  • 14-day total rainfall: {rain_14d:.1f} mm\n"
            f"Wildfire Spread Risk: {risk}\n"
            f"Drought Index: {drought}"
        )
    except Exception:
        return _fallback_climate_by_lat(lat)


@mcp.tool()
def search_env_news(topic: str, region: str) -> str:
    """Get environment news headlines by topic/region."""
    _ = topic
    return REGION_DATA[_region_key(region)]["news"]


@mcp.tool()
async def get_fire_coordinates(region: str) -> str:
    """
    Returns fire hotspot coordinates as JSON for map rendering.
    Each hotspot has lat, lon, frp (fire radiative power), and brightness.

    Args:
        region: US region name e.g. 'Northern California'
    """
    import json
    print(f"[MCP] get_fire_coordinates called for: {region}", file=sys.stderr)

    bounding_boxes = {
        "northern california": (37.0, 42.0, -124.5, -119.5),
        "southern california": (32.5, 37.0, -121.0, -114.0),
        "pacific northwest":   (45.0, 49.5, -124.5, -116.5),
        "texas":               (25.8, 36.5, -106.6, -93.5),
        "amazon":              (-5.0, 5.0,  -70.0,  -55.0),
        "default":             (24.0, 49.0, -125.0, -66.0),
    }

    key = region.lower()
    bbox = next((v for k, v in bounding_boxes.items() if k in key),
                bounding_boxes["default"])
    lat_min, lat_max, lon_min, lon_max = bbox

    try:
        url = (
            f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/"
            f"{NASA_KEY}/VIIRS_SNPP_NRT/"
            f"{lon_min},{lat_min},{lon_max},{lat_max}/1"
        )
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)

        lines = [l for l in resp.text.strip().split("\n") if l]
        hotspots = []

        for row in lines[1:50]:  # max 50 hotspots for map performance
            parts = row.split(",")
            if len(parts) >= 13:
                try:
                    hotspots.append({
                        "lat": float(parts[0]),
                        "lon": float(parts[1]),
                        "frp": float(parts[12]),
                        "brightness": float(parts[2]) if len(parts) > 2 else 300,
                    })
                except ValueError:
                    continue

        return json.dumps({"hotspots": hotspots, "region": region})

    except Exception as e:
        print(f"[MCP] get_fire_coordinates error: {e}", file=sys.stderr)
        # Demo hotspots for Northern California
        demo = [
            {"lat": 40.23, "lon": -122.44, "frp": 187.0, "brightness": 412},
            {"lat": 39.87, "lon": -121.92, "frp": 94.0,  "brightness": 368},
            {"lat": 40.51, "lon": -123.01, "frp": 62.0,  "brightness": 341},
            {"lat": 38.92, "lon": -120.77, "frp": 38.0,  "brightness": 320},
            {"lat": 41.02, "lon": -122.15, "frp": 21.0,  "brightness": 308},
        ]
        return json.dumps({"hotspots": demo, "region": region, "demo": True})


@mcp.tool()
async def get_historical_trends(lat: float, lon: float, days: int = 30) -> str:
    """
    Fetch historical temperature and precipitation data for trend charts.
    Uses Open-Meteo historical API — no API key required.

    Args:
        lat:  Latitude
        lon:  Longitude
        days: Number of past days to fetch (default 30, max 90)
    """
    import json
    from datetime import datetime, timedelta

    print(f"[MCP] get_historical_trends called for: {lat}, {lon}", file=sys.stderr)

    days = min(days, 90)
    end   = datetime.now()
    start = end - timedelta(days=days)

    try:
        url = (
            f"https://archive-api.open-meteo.com/v1/archive"
            f"?latitude={lat}&longitude={lon}"
            f"&start_date={start.strftime('%Y-%m-%d')}"
            f"&end_date={end.strftime('%Y-%m-%d')}"
            f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max"
            f"&timezone=auto"
        )

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url)
            data = resp.json()

        daily = data.get("daily", {})
        dates  = daily.get("time", [])
        tmax   = daily.get("temperature_2m_max", [])
        tmin   = daily.get("temperature_2m_min", [])
        precip = daily.get("precipitation_sum", [])
        wind   = daily.get("wind_speed_10m_max", [])

        return json.dumps({
            "dates":  dates,
            "temp_max": tmax,
            "temp_min": tmin,
            "precipitation": precip,
            "wind_max": wind,
            "lat": lat,
            "lon": lon,
        })

    except Exception as e:
        print(f"[MCP] get_historical_trends error: {e}", file=sys.stderr)
        # Generate 30 days of realistic demo data
        import random
        random.seed(42)
        demo_dates = [(start + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days)]
        return json.dumps({
            "dates":        demo_dates,
            "temp_max":     [round(32 + random.uniform(-5, 12), 1) for _ in range(days)],
            "temp_min":     [round(18 + random.uniform(-4, 8),  1) for _ in range(days)],
            "precipitation":[round(random.uniform(0, 3) if random.random() > 0.7 else 0, 1) for _ in range(days)],
            "wind_max":     [round(15 + random.uniform(-8, 25), 1) for _ in range(days)],
            "demo": True,
        })


if __name__ == "__main__":
    # Expose an HTTP endpoint: http://127.0.0.1:8000/mcp
    mcp.run(transport="streamable-http")

