from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import requests

from app.news import get_news

app = FastAPI(title="News Aggregator API")


app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )


@app.get("/news")
def news(
    category: str | None = None,
    source: str | None = None,
    limit: int = 50
):
    return get_news(
        category=category,
        source=source,
        limit=limit
    )

@app.get("/weather")
def weather(latitude: float, longitude: float):

    # Get weather
    weather_url = "https://api.open-meteo.com/v1/forecast"

    weather_params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "apparent_temperature,"
            "weather_code,"
            "wind_speed_10m"
        ),
        "daily": (
            "temperature_2m_max,"
            "temperature_2m_min,"
            "weather_code"
        ),
        "temperature_unit": "fahrenheit",
        "wind_speed_unit": "mph",
        "timezone": "auto"
    }

    weather_response = requests.get(
        weather_url,
        params=weather_params,
        timeout=10
    )

    weather_response.raise_for_status()

    weather_data = weather_response.json()

    # Reverse geocoding
    location_url = "https://nominatim.openstreetmap.org/reverse"

    location_params = {
        "lat": latitude,
        "lon": longitude,
        "format": "json",
        "zoom": 10
    }

    location_headers = {
        "User-Agent": "NewsAggregator/1.0"
    }

    location_response = requests.get(
        location_url,
        params=location_params,
        headers=location_headers,
        timeout=10
    )

    location_response.raise_for_status()

    location_data = location_response.json()

    print("LOCATION DATA:")
    print(location_data)

    address = location_data.get("address", {})

    town = (
        address.get("town")
        or address.get("city")
        or address.get("village")
        or address.get("municipality")
        or address.get("county")
        or "Unknown Location"
    )

    print("TOWN:", town)

    weather_data["location_name"] = town

    return weather_data