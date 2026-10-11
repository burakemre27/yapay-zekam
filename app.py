import streamlit as st
import requests
from groq import Groq
from duckduckgo_search import DDGS

st.set_page_config(page_title="Canlı Asistanım", page_icon="🌐")
st.title("🌐 Canlı Veri Destekli Kişisel Asistanım")

API_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=API_KEY)

# 1. Modeli arka planda otomatik belirle (Kenar çubuğu olmadan)
@st.cache_data(ttl=3600)
def get_best_model():
    try:
        model_list = client.models.list()
        valid = [
            m.id for m in model_list.data 
            if not any(x in m.id.lower() for x in ["whisper", "embed", "guard", "safetensors"])
        ]
        # Öncelik: Llama 8b (hızlı) veya 70b (güçlü)
        for pref in ["llama-3.1-8b-instant", "llama3-8b-8192", "llama-3.3-70b-versatile"]:
            if pref in valid:
                return pref
        return valid[0] if valid else "llama-3.3-70b-versatile"
    except Exception:
        return "llama-3.3-70b-versatile"

selected_model = get_best_model()

# 2. Canlı hava durumu fonksiyonu (Open-Meteo API)
def get_live_weather(city_name):
    try:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1&language=tr&format=json"
        geo_res = requests.get(geo_url, timeout=5).json()
        if not geo_res.get("results"):
            return None
        
        loc = geo_res["results"][0]
        lat, lon = loc["latitude"], loc["longitude"]
        city_display = f"{loc['name']}, {loc.get('country', '')}"

        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,wind_speed_10m&timezone=auto"
        w_res = requests.get(weather_url, timeout=5).json()
        curr = w_res.get("current", {})

        return (
            f"CANLI HAVA DURUMU ({city_display}):\n"
            f"- Sıcaklık: {curr.get('temperature_2m')} °C\n"
            f"- Hissedilen: {curr.get('apparent_temperature')} °C\n"
            f"- Nem: %{curr.get('relative_humidity_2m')}\n"
            f"- Rüzgar Hızı: {curr.get('wind_speed_10m')} km/s"
        )
    except Exception:
        return None

# 3. DuckDuckGo web araması
def search_web(query):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
            if not results:
                return ""
            snippets = [f"{r.get('title')}: {r.get('body')}" for r in results if r.get('body')]
            return "\n".join(snippets)[:2000]
    except Exception:
        return ""

# Sohbet geçmişini başlat
if "messages" not in st.session_state:
    st.session_state.messages = []
