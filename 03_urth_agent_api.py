from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamable_http_client
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import FileResponse, JSONResponse
from starlette.routing import Route

BASE_DIR = Path(__file__).resolve().parent
HTML_PATH = BASE_DIR / "urth_agent.html"
MCP_URL = "http://127.0.0.1:8000/mcp"

REGION_ARGS = {
    "Northern California": {"city": "Sacramento", "lat": 39.5, "lon": -121.5},
    "Amazon Basin": {"city": "Manaus", "lat": -3.4, "lon": -65.0},
    "Florida": {"city": "Miami", "lat": 25.8, "lon": -80.2},
}


def _content_to_text(content: object) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            text = getattr(item, "text", None)
            if text:
                parts.append(str(text))
        if parts:
            return "\n".join(parts)
    return str(content)


def _risk_from_data(fire: str, air: str, climate: str) -> str:
    joined = f"{fire}\n{air}\n{climate}".upper()
    if "EXTREME" in joined:
        return "EXTREME"
    if "UNHEALTHY" in joined or "SEVERE" in joined or "HIGH" in joined:
        return "HIGH"
    if "MODERATE" in joined:
        return "MODERATE"
    return "LOW"


def _build_report(region: str, risk: str, fire: str, air: str, climate: str, news: str) -> str:
    ts = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S UTC")
    return (
        f"ENVIRONMENTAL RISK ASSESSMENT — {region}\n"
        f"Generated: {ts}\n\n"
        f"OVERALL RISK LEVEL: {risk}\n\n"
        "KEY FINDINGS\n\n"
        f"Wildfire (NASA FIRMS):\n{fire}\n\n"
        f"Air Quality (OpenAQ v3):\n{air}\n\n"
        f"Climate Risk (Open-Meteo):\n{climate}\n\n"
        f"News Context:\n{news}\n"
    )


async def run_pipeline(request: Request) -> JSONResponse:
    payload = await request.json()
    region = payload.get("region", "Northern California")
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

    fire_text = _content_to_text(fire_result.content)
    air_text = _content_to_text(air_result.content)
    climate_text = _content_to_text(climate_result.content)
    news_text = _content_to_text(news_result.content)
    risk = _risk_from_data(fire_text, air_text, climate_text)
    report = _build_report(region, risk, fire_text, air_text, climate_text, news_text)

    return JSONResponse(
        {
            "region": region,
            "risk": risk,
            "raw": {
                "fire": fire_text,
                "air": air_text,
                "climate": climate_text,
                "news": news_text,
            },
            "mcp_calls": [
                {"tool": "get_active_fires", "args": {"region": region}, "result": fire_text},
                {"tool": "get_air_quality", "args": {"city": args["city"]}, "result": air_text},
                {"tool": "get_weather_risk", "args": {"lat": args["lat"], "lon": args["lon"]}, "result": climate_text},
                {"tool": "search_env_news", "args": {"topic": "wildfire", "region": region}, "result": news_text},
            ],
            "report": report,
        }
    )


async def home(_: Request) -> FileResponse:
    return FileResponse(HTML_PATH)


app = Starlette(
    debug=True,
    routes=[
        Route("/", home, methods=["GET"]),
        Route("/api/run", run_pipeline, methods=["POST"]),
    ],
)

