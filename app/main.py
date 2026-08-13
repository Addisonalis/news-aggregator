from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import requests

from app.news import get_news
from app.database import initialize_database


app = FastAPI(title="News Aggregator API")


# Initialize database when the application starts
initialize_database()


# Static files
app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


# Templates
templates = Jinja2Templates(directory="templates")


# -------------------------
# Home page
# -------------------------

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )


# -------------------------
# News
# -------------------------

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


# -------------------------
# Weather
# -------------------------

@app.get("/weather")
def weather(latitude: float, longitude: float):

    # Get weather from Open-Meteo
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


    # -------------------------
    # Get town/city name
    # -------------------------

    location_url = "https://nominatim.openstreetmap.org/reverse"

    location_params = {
        "lat": latitude,
        "lon": longitude,
        "format": "json",
        "zoom": 10
    }

    try:

        location_response = requests.get(
            location_url,
            params=location_params,
            headers={
                "User-Agent": "NewsAggregator/1.0"
            },
            timeout=5
        )

        if location_response.status_code == 200:

            location_data = location_response.json()

            address = location_data.get("address", {})

            town = (
                address.get("town")
                or address.get("city")
                or address.get("village")
                or address.get("municipality")
                or "Local Weather"
            )

        else:

            town = "Local Weather"

    except requests.RequestException:

        town = "Local Weather"


    # Add town name to response
    weather_data["location_name"] = town

    return weather_data