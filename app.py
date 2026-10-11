import streamlit as st
import requests
import time
from groq import Groq
from duckduckgo_search import DDGS

# Sayfa yapılandırması
st.set_page_config(
    page_title="Tegmen'S JARVİS // Kişisel Asistan",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Yüksek Teknolojili Siber CSS Stili
st.markdown(
    """
    <style>
        /* Genel Arka Plan ve Yazı Tipi */
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;800&family=Orbitron:wght@500;700;900&display=swap');
        
        .stApp {
            background: radial-gradient(circle at 50% 0%, #0d1527 0%, #060913 60%, #030408 100%);
            color: #d1e4ff;
            font-family: 'JetBrains Mono', monospace;
        }

        /* Kenar çubuğunu gizle */
        [data-testid="stSidebar"], [data-testid="stSidebarNav"], button[kind="header"] {
            display: none !important;
        }

        /* Üst Panel (Header Banner) */
        .tech-header {
            border: 1px solid rgba(0, 243, 255, 0.2);
            background: rgba(10, 20, 40, 0.6);
            backdrop-filter: blur(12px);
            padding: 22px 28px;
            border-radius: 16px;
            box-shadow: 0 0 25px rgba(0, 243, 255, 0.08);
            margin-bottom: 25px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .tech-title {
            font-family: 'Orbitron', sans-serif;
            font-size: 26px;
            font-weight: 800;
            background: linear-gradient(90deg, #00f3ff, #0077fe, #a855f7);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: 2px;
            margin: 0;
        }

        .status-badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 11px;
            letter-spacing: 1.5px;
            font-weight: 700;
            background: rgba(16, 185, 129, 0.12);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.35);
            box-shadow: 0 0 12px rgba(16, 185, 129, 0.25);
        }

        .status-dot {
            width: 8px;
            height: 8px;
            background-color: #34d399;
            border-radius: 50%;
            animation: pulse 1.8s infinite;
        }

        @keyframes pulse {
            0% { transform: scale(0.9); opacity: 0.6; }
            50% { transform: scale(1.3); opacity: 1; box-shadow: 0 0 8px #34d399; }
            100% { transform: scale(0.9); opacity: 0.6; }
        }

        /* Mesaj Balonları */
        [data-testid="stChatMessage"] {
            border-radius: 14px;
            padding: 16px 20px;
            margin-bottom: 14px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
        }

        /* Kullanıcı Mesajı */
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
            background: rgba(14, 30, 60, 0.45) !important;
            border: 1px solid rgba(0, 243, 255, 0.25);
            box-shadow: 0 0 15px rgba(0, 243, 255, 0.05);
        }

        /* Asistan Mesajı */
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
            background: rgba(18, 22, 38, 0.65) !important;
            border: 1px solid rgba(168, 85, 247, 0.25);
            box-shadow: 0 0 15px rgba(168, 85, 247, 0.05);
        }

        /* Giriş Çubuğu (Chat Input) */
        [data-testid="stChatInput"] {
            border-radius: 14px !important;
            border: 1px solid rgba(0, 243, 255, 0.3) !important;
            background: rgba(10, 16, 32, 0.8) !important;
            box-shadow: 0 0 20px rgba(0, 243, 255, 0.1) !important;
        }

        [data-testid="stChatInput"]:focus-within {
            border-color: #00f3ff !important;
            box-shadow: 0 0 25px rgba(0, 243, 255, 0.3) !important;
        }

        /* Canlı Veri Bilgi Kutusu */
        .live-chip {
            display: inline-block;
            font-size: 11px;
            color: #00f3ff;
            background: rgba(0, 243, 255, 0.08);
            border: 1px solid rgba(0, 243, 255, 0.2);
            padding: 2px 8px;
            border-radius: 6px;
            margin-bottom: 8px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

API_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=API_KEY)

# 1. En Uygun Modeli Arka Planda Seç
@st.cache_data(ttl=3600)
def get_best_model():
    try:
        model_list = client.models.list()
        valid = [
            m.id for m in model_list.data 
            if not any(x in m.id.lower() for x in ["whisper", "embed", "guard", "safetensors"])
        ]
        for pref in ["llama-3.1-8b-instant", "llama3-8b-8192", "llama-3.3-70b-versatile"]:
            if pref in valid:
                return pref
        return valid[0] if valid else "llama-3.3-70b-versatile"
    except Exception:
        return "llama-3.3-70b-versatile"

selected_model = get_best_model()

# 2. Canlı Hava Durumu (Open-Meteo)
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
            f"CANLI TELEMETRİ ({city_display}):\n"
            f"- Sıcaklık: {curr.get('temperature_2m')} °C\n"
            f"- Hissedilen: {curr.get('apparent_temperature')} °C\n"
            f"- Bağıl Nem: %{curr.get('relative_humidity_2m')}\n"
            f"- Rüzgar Hızı: {curr.get('wind_speed_10m')} km/s"
        )
    except Exception:
        return None

# 3. DuckDuckGo Web Taraması
def search_web(query):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
            if not results:
                return ""
            snippets = [f"[{r.get('title')}]: {r.get('body')}" for r in results if r.get('body')]
            return "\n".join(snippets)[:2000]
    except Exception:
        return ""

# Üst Teknoloji Paneli
st.markdown(
    f"""
    <div class="tech-header">
        <div>
            <div class="tech-title">⚡ NEXUS CORE // v3.2</div>
            <div style="font-size: 12px; color: #7f97b5; margin-top: 4px;">MOTOR: {selected_model.upper()} | DÜŞÜK GECİKME</div>
        </div>
        <div class="status-badge">
            <span class="status-dot"></span> ÇEVRİMİÇİ // GERÇEK ZAMANLI
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Mesaj Geçmişini Listele
for msg in st.session_state.messages:
    role = msg["role"]
    avatar = "🧑‍💻" if role == "user" else "⚡"
    with st.chat_message(role, avatar=avatar):
        st.markdown(msg["content"])

# Yeni İstek
if prompt := st.chat_input("Sorgu veya komut girin (örn: Ankara hava durumu)..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="⚡"):
        with st.spinner("CANLI VERİ AKIŞI SAĞLANIYOR..."):
            extra_context = ""
            prompt_lower = prompt.lower()
            
            # Hava Durumu Telemetrisi
            if any(w in prompt_lower for w in ["hava", "derece", "sıcaklık", "yağmur"]):
                cities = ["ankara", "istanbul", "izmir", "bursa", "antalya", "konya", "adana", "trabzon", "eskişehir", "gaziantep"]
                for city in cities:
                    if city in prompt_lower:
                        extra_context = get_live_weather(city)
                        break
            
            # Web Araması
            if not extra_context:
                extra_context = search_web(prompt)

            system_instruction = (
                "Sen fütüristik, zeki, doğrudan ve yüksek analitik kabiliyete sahip Türkçe bir yapay zeka çekirdeğisin. "
                "Cevaplarını net, profesyonel, modern ve akıcı bir Türkçe ile sun. Gereksiz dolambaçlı laflar etme. "
                "Sana iletilen 'CANLI TELEMETRİ / VERİ' bilgilerini kesin gerçek kabul ederek kullanıcıyı anında bilgilendir."
            )
            if extra_context:
                system_instruction += f"\n\nCANLI VERİ KAYNAĞI:\n{extra_context}\n\nBu veriyi kullanarak yanıt üret."

            payload = [{"role": "system", "content": system_instruction}]
            for m in st.session_state.messages[-6:]:
                payload.append({"role": m["role"], "content": m["content"]})

            try:
                # Gerçek zamanlı daktilo akışı (Stream)
                response_stream = client.chat.completions.create(
                    model=selected_model,
                    messages=payload,
                    temperature=0.4,
                    stream=True
                )
                
                # Canlı veri geldiyse küçük neon etiket göster
                if extra_context:
                    st.markdown("<span class=\"live-chip\">⚡ CANLI AĞ VERİSİ ENTEGRE EDİLDİ</span>", unsafe_allow_html=True)
                
                # Kelime kelime ekrana dök
                response_placeholder = st.empty()
                full_response = ""
                for chunk in response_stream:
                    token = chunk.choices[0].delta.content or ""
                    full_response += token
                    response_placeholder.markdown(full_response + " ▌")
                
                response_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})

            except Exception as e:
                st.error(f"SİSTEM ÇEKİRDEK HATASI: {str(e)}")
