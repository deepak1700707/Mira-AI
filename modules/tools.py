from langchain.tools import tool
import requests, os, json
import requests
import webbrowser
import datetime
import os

CONFIG_PATH = os.path.join("data", "config.json")
CONFIG = json.load(open(CONFIG_PATH)) if os.path.exists(CONFIG_PATH) else {}

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

# @tool
# def web_search(query: str) -> str:
#     """Perform a web search using Tavily."""
#     tavily_key = CONFIG.get("tavily_api_key", "")
#     if not tavily_key:
#         return "❌ Tavily API key missing."
#     headers = {"Authorization": f"Bearer {tavily_key}"}
#     payload = {"query": query, "num_results": 3}
#     res = requests.post("https://api.tavily.com/search", headers=headers, json=payload).json()
#     results = res.get("results", [])
#     if not results:
#         return "No results found."
#     summary = "\n".join([f"- {r['title']}: {r['url']}" for r in results])
#     return summary

# @tool
# def get_time():
#     """Get the current system time."""
#     from datetime import datetime
#     return datetime.now().strftime("%I:%M %p")


# # 🖥️ System Commands
# @tool
# def open_youtube():
#     webbrowser.open("https://www.youtube.com")
#     return "Opening YouTube..."

# @tool
# def open_browser(url="https://google.com"):
#     webbrowser.open(url)
#     return f"Opening {url}"

# # ⏰ Time tool
# @tool
# def get_time():
#     now = datetime.datetime.now().strftime("%I:%M %p")
#     return f"The current time is {now}."

# # 🗣️ Example for custom tool
# @tool
# def tell_joke():
#     jokes = [
#         "Why did the AI go to school? To improve its neural network!",
#         "I tried to catch fog yesterday — I mist!"
#     ]
#     import random
#     return random.choice(jokes)