"""OpenWeatherMap API wrapper + smart agriculture advice generator."""
import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


def get_weather(city: str) -> dict:
    """Fetch current weather for a city. Returns structured weather dict."""
    if not API_KEY or API_KEY == "your_api_key_here":
        # Demo mode: return realistic mock data
        return _mock_weather(city)

    try:
        resp = requests.get(BASE_URL, params={
            "q": city, "appid": API_KEY, "units": "metric"
        }, timeout=8)
        resp.raise_for_status()
        data = resp.json()
        return _parse_weather(data)
    except requests.exceptions.HTTPError as e:
        if resp.status_code == 401:
            # Key registered but not yet activated (can take up to 2 hours for new keys)
            # Fall back to demo mode so the app remains usable
            result = _mock_weather(city)
            result["key_pending"] = True
            return result
        if resp.status_code == 404:
            return {"error": f"City '{city}' not found. Please check the spelling."}
        return {"error": str(e)}
    except requests.exceptions.RequestException as e:
        return {"error": f"Network error: {str(e)}"}


def _parse_weather(data: dict) -> dict:
    main     = data.get("main", {})
    wind     = data.get("wind", {})
    weather  = data.get("weather", [{}])[0]
    rain_1h  = data.get("rain", {}).get("1h", 0)

    result = {
        "city":        data.get("name", "Unknown"),
        "country":     data.get("sys", {}).get("country", ""),
        "temp":        round(main.get("temp", 0), 1),
        "feels_like":  round(main.get("feels_like", 0), 1),
        "humidity":    main.get("humidity", 0),
        "pressure":    main.get("pressure", 0),
        "description": weather.get("description", "").title(),
        "icon":        weather.get("icon", "01d"),
        "wind_speed":  round(wind.get("speed", 0), 1),
        "rainfall_1h": rain_1h,
        "visibility":  round(data.get("visibility", 10000) / 1000, 1),
    }
    result["advice"] = _generate_advice(result)
    result["alerts"]  = _generate_alerts(result)
    return result


def _mock_weather(city: str) -> dict:
    """Return demo weather data when no API key is configured."""
    result = {
        "city":        city.title(),
        "country":     "IN",
        "temp":        28.5,
        "feels_like":  31.2,
        "humidity":    82,
        "pressure":    1010,
        "description": "Partly Cloudy",
        "icon":        "02d",
        "wind_speed":  4.2,
        "rainfall_1h": 0,
        "visibility":  9.0,
        "demo_mode":   True,
    }
    result["advice"] = _generate_advice(result)
    result["alerts"]  = _generate_alerts(result)
    return result


def _generate_advice(w: dict) -> dict:
    """Generate smart irrigation and fertilizer advice based on weather."""
    advice = {}

    # Irrigation advice
    if w["rainfall_1h"] > 5:
        advice["irrigation"] = {
            "action": "Skip Irrigation",
            "reason": f"Heavy rainfall ({w['rainfall_1h']}mm/hr detected). Save water today.",
            "icon": "💧", "status": "warning"
        }
    elif w["humidity"] > 85:
        advice["irrigation"] = {
            "action": "Reduce Irrigation",
            "reason": f"High humidity ({w['humidity']}%) — soil evaporation is low.",
            "icon": "💧", "status": "info"
        }
    elif w["temp"] > 35:
        advice["irrigation"] = {
            "action": "Irrigate in Early Morning",
            "reason": f"High temperature ({w['temp']}°C) — avoid midday irrigation to reduce evaporation.",
            "icon": "💧", "status": "action"
        }
    else:
        advice["irrigation"] = {
            "action": "Normal Irrigation Schedule",
            "reason": "Weather conditions are suitable for regular irrigation.",
            "icon": "💧", "status": "good"
        }

    # Fertilizer advice
    if w["rainfall_1h"] > 2 or w["wind_speed"] > 8:
        advice["fertilizer"] = {
            "action": "Avoid Fertilizer Application",
            "reason": "Rain or strong wind will wash away fertilizer, causing waste and pollution.",
            "icon": "🌿", "status": "warning"
        }
    elif w["temp"] < 15:
        advice["fertilizer"] = {
            "action": "Delay Fertilizer Application",
            "reason": f"Low temperature ({w['temp']}°C) — plant nutrient uptake is reduced.",
            "icon": "🌿", "status": "info"
        }
    else:
        advice["fertilizer"] = {
            "action": "Good Time for Fertilization",
            "reason": "Weather is ideal for fertilizer application and nutrient uptake.",
            "icon": "🌿", "status": "good"
        }

    # Pest risk
    if w["humidity"] > 80 and w["temp"] > 22:
        advice["pest"] = {
            "action": "Monitor for Fungal Diseases",
            "reason": f"High humidity ({w['humidity']}%) + warm temperature ({w['temp']}°C) creates ideal conditions for fungal growth.",
            "icon": "🐛", "status": "warning"
        }
    else:
        advice["pest"] = {
            "action": "Low Pest Risk",
            "reason": "Current conditions do not favor major pest or disease outbreaks.",
            "icon": "🐛", "status": "good"
        }

    return advice


def _generate_alerts(w: dict) -> list:
    """Generate farmer alert messages."""
    alerts = []
    if w["rainfall_1h"] > 10:
        alerts.append({"level": "danger", "msg": "⛈️ Heavy rain expected — avoid all field activities today"})
    if w["temp"] > 40:
        alerts.append({"level": "danger", "msg": "🌡️ Extreme heat warning — protect sensitive crops and livestock"})
    if w["wind_speed"] > 10:
        alerts.append({"level": "warning", "msg": "💨 Strong winds — skip spraying pesticides or fertilizers"})
    if w["humidity"] > 90:
        alerts.append({"level": "warning", "msg": "💦 Very high humidity — watch for fungal/blight disease outbreaks"})
    if w["temp"] < 10:
        alerts.append({"level": "info", "msg": "🥶 Low temperature — protect frost-sensitive crops overnight"})
    return alerts
