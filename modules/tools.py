from langchain.tools import tool
import requests
import datetime
from utils.config import CONFIG

@tool("Get current weather info for a given city")
def get_weather(city: str) -> str:
    """Get current weather info for a given city."""
    api_key = CONFIG.get("openweather_api_key", "")
    if not api_key:
        return "❌ Weather API key missing."
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    r = requests.get(url)
    data = r.json()
    if data.get("cod") != 200:
        return f"City not found: {city}"
    temp = data["main"]["temp"]
    desc = data["weather"][0]["description"]
    return f"{city.title()} का तापमान {temp}°C है और मौसम {desc} है।"

@tool
def get_time() -> str:
    """Get the current system time."""
    now = datetime.datetime.now().strftime("%I:%M %p")
    return f"The current time is {now}."