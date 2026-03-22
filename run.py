import asyncio
from datetime import datetime, timezone

from flask import Flask, jsonify, request
from flask_cors import CORS
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamable_http_client
from mcp.client.stdio import stdio_client, StdioServerParameters
from alerts import send_alert
app = Flask(__name__)
CORS(app)

MCP_URL = "http://127.0.0.1:8000/mcp"
REGION_ARGS = {
    "Northern California": {"city": "Sacramento", "lat": 39.5, "lon": -121.5},
    "Amazon Basin": {"city": "Manaus", "lat": -3.4, "lon": -65.0},
    "Florida": {"city": "Miami", "lat": 25.8, "lon": -80.2},
    "Texas": {"city": "Austin", "lat": 30.27, "lon": -97.74},
    "Southern California": {"city": "Los Angeles", "lat": 34.05, "lon": -118.24},
    "Pacific Northwest": {"city": "Seattle", "lat": 47.60, "lon": -122.33},
}


def _content_to_text(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            text = getattr(item, "text", None)
            if text:
                parts.append(str(text))
        if parts:
            return "\n".join(parts)
    return str(content)


def _risk_from_data(fire, air, climate):
    joined = f"{fire}\n{air}\n{climate}".upper()
    if "EXTREME" in joined:
        return "EXTREME"
    if "UNHEALTHY" in joined or "SEVERE" in joined or "HIGH" in joined:
        return "HIGH"
    if "MODERATE" in joined:
        return "MODERATE"
    return "LOW"


def _build_report(region, risk, fire, air, climate, news):
    ts = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S UTC")
    return (
        f"ENVIRONMENTAL RISK ASSESSMENT - {region}\n"
        f"Generated: {ts}\n\n"
        f"OVERALL RISK LEVEL: {risk}\n\n"
        "KEY FINDINGS\n\n"
        f"Wildfire (NASA FIRMS):\n{fire}\n\n"
        f"Air Quality (OpenAQ v3):\n{air}\n\n"
        f"Climate Risk (Open-Meteo):\n{climate}\n\n"
        f"News Context:\n{news}\n"
    )


async def run_agent(query, region):
    _ = query
    args = REGION_ARGS.get(region, REGION_ARGS["Northern California"])
    async with streamable_http_client(MCP_URL) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            fire_result = await session.call_tool("get_active_fires", {"region": region})
            air_result = await session.call_tool("get_air_quality", {"city": args["city"]})
            climate_result = await session.call_tool(
                "get_weather_risk", {"lat": args["lat"], "lon": args["lon"]}
            )
            news_result = await session.call_tool("search_env_news", {"topic": "wildfire", "region": region})

    fire_data = _content_to_text(fire_result.content)
    air_data = _content_to_text(air_result.content)
    climate_data = _content_to_text(climate_result.content)
    news_data = _content_to_text(news_result.content)
    risk = _risk_from_data(fire_data, air_data, climate_data)
    report = _build_report(region, risk, fire_data, air_data, climate_data, news_data)
    return {
        "report": report,
        "fire_data": fire_data,
        "air_data": air_data,
        "climate_data": climate_data,
        "news_data": news_data,
        "risk": risk,
    }


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json or {}
    region = data.get("region", "Northern California")
    query = data.get("query", f"Full environmental risk assessment for {region}")
    result = asyncio.run(run_agent(query=query, region=region))
    return jsonify(result)


@app.route("/fire-map", methods=["POST"])
def fire_map():
    """Returns fire hotspot coordinates for the map."""
    import json
    data   = request.json
    region = data.get("region", "Northern California")

    async def _get():
        server_params = StdioServerParameters(command="python", args=["01_basic_server.py"])
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(
                    "get_fire_coordinates", arguments={"region": region}
                )
                return result.content[0].text

    raw = asyncio.run(_get())
    return jsonify(json.loads(raw))


@app.route("/trends", methods=["POST"])
def trends():
    import json
    data = request.json
    lat  = data.get("lat", 39.5)
    lon  = data.get("lon", -121.5)
    days = data.get("days", 30)

    async def _get():
        server_params = StdioServerParameters(command="python", args=["01_basic_server.py"])
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(
                    "get_historical_trends",
                    arguments={"lat": lat, "lon": lon, "days": days}
                )
                return result.content[0].text

    raw = asyncio.run(_get())
    return jsonify(json.loads(raw))


@app.route("/send-alert", methods=["POST"])
def trigger_alert():
    data       = request.json
    region     = data.get("region", "")
    risk_level = data.get("risk_level", "")
    report     = data.get("report", "")
    fire_data  = data.get("fire_data", "")
    air_data   = data.get("air_data", "")

    from alerts import send_alert
    result = send_alert(region, risk_level, report, fire_data, air_data)
    return jsonify(result)


if __name__ == "__main__":
    print("Starting Urth Agent backend on http://localhost:5000")
    app.run(port=5000, debug=True)

