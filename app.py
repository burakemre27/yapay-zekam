import streamlit as st
import requests
from groq import Groq
from duckduckgo_search import DDGS

st.set_page_config(page_title="Tegmen YILMAZ", page_icon="🌐")
st.title("🌐 Tegmen's Jarvis")

API_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=API_KEY)

# 1. Aktif modelleri al
@st.cache_data(ttl=3600)
def get_available_chat_models():
    try:
        model_list = client.models.list()
        valid = [
            m.id for m in model_list.data 
            if not any(x in m.id.lower() for x in ["whisper", "embed", "guard", "safetensors"])
        ]
        return valid if valid else ["llama-3.3-70b-versatile"]
    except Exception:
        return ["llama-3.3-70b-versatile"]

models = get_available_chat_models()
selected_model = st.sidebar.selectbox("Kullanılan Model", models, index=0)

# 2. Şehirlerin anlık hava durumunu garantili çeken ücretsiz fonksiyon (Open-Meteo API)
def get_live_weather(city_name):
    try:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1&language=tr&format=json"
        geo_res = requests.get(geo_url, timeout=5).json()
        if not geo_res.get("results"):
            return None
        
        loc = geo_res["results"][0]
        lat, lon = loc["latitude"], loc["longitude"]
        city_display = f"{loc['name']}, {loc.get('country', '')}"

        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m&timezone=auto"
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

# 3. Genel DuckDuckGo web araması
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

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Bir şeyler sorun (örneğin: Ankara hava durumu)..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Canlı veriler kontrol ediliyor..."):
            extra_context = ""
            
            # Hava durumu sorusu mu tespit et
            prompt_lower = prompt.lower()
            if any(w in prompt_lower for w in ["hava", "derece", "sıcaklık", "yağmur"]):
                # Cümleden şehri tahmin etmeye çalış
                for city in ["ankara", "istanbul", "izmir", "bursa", "antalya", "konya", "adana"]:
                    if city in prompt_lower:
                        weather_data = get_live_weather(city)
                        if weather_data:
                            extra_context = weather_data
                        break
            
            # Eğer hava durumu değilse veya bulunamadıysa DuckDuckGo ara
            if not extra_context:
                extra_context = search_web(prompt)

            system_instruction = (
                "Sen internetten anlık veri alma yeteneği olan Türkçe bir asistansın. "
                "Sana verilen 'CANLI VERİ' bilgilerini kesin gerçek kabul ederek kullanıcıya doğrudan, net ve güncel yanıt ver."
            )
            if extra_context:
                system_instruction += f"\n\nCANLI VERİ:\n{extra_context}\n\nBu veriyi temel alarak cevap ver."

            payload = [{"role": "system", "content": system_instruction}]
            for m in st.session_state.messages[-6:]:
                payload.append({"role": m["role"], "content": m["content"]})

            try:
                completion = client.chat.completions.create(
                    model=selected_model,
                    messages=payload,
                    temperature=0.4,
                )
                response_text = completion.choices[0].message.content
                st.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})
            except Exception as e:
                st.error(f"Hata: {str(e)}")
