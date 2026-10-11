import streamlit as st
import requests
import re
from groq import Groq

# Sayfa yapılandırması
st.set_page_config(
    page_title="Tegmen AI",
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
            padding: 3px 10px;
            border-radius: 6px;
            margin-bottom: 8px;
            letter-spacing: 1px;
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

# 2. Küresel Dinamik Canlı Hava Durumu (Open-Meteo)
def get_live_weather(query_text):
    try:
        clean_name = re.sub(
            r'\b(hava|durumu|kaç|derece|sıcaklık|yağmur|kar|rüzgar|nasıl|bugün|anlık|için|da|de|te|ta)\b', 
            '', 
            query_text, 
            flags=re.IGNORECASE
        ).strip()
        
        target = clean_name if clean_name else query_text
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={target}&count=1&format=json"
        geo_res = requests.get(geo_url, timeout=5).json()
        
        if not geo_res.get("results"):
            return None
        
        loc = geo_res["results"][0]
        lat, lon = loc["latitude"], loc["longitude"]
        city_display = f"{loc['name']}, {loc.get('admin1', '')} ({loc.get('country', '')})"

        weather_url = (
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
            f"&current=temperature_2m,relative_humidity_2m,apparent_temperature,wind_speed_10m&timezone=auto"
        )
        w_res = requests.get(weather_url, timeout=5).json()
        curr = w_res.get("current", {})

        return (
            f"KÜRESEL TELEMETRİ ({city_display}):\n"
            f"- Sıcaklık: {curr.get('temperature_2m')} °C\n"
            f"- Hissedilen Sıcaklık: {curr.get('apparent_temperature')} °C\n"
            f"- Bağıl Nem: %{curr.get('relative_humidity_2m')}\n"
            f"- Rüzgar Hızı: {curr.get('wind_speed_10m')} km/s"
        )
    except Exception:
        return None

# 3. Genel İnternet Taraması (Wikipedia + DuckDuckGo Hibrit)
def search_general_web(query):
    results = []
    
    # Katman A: Wikipedia Özet API (Bilim, tarih, edebiyat, teknoloji için hızlı ve güvenilir)
    try:
        wiki_url = f"https://tr.wikipedia.org/api/rest_v1/page/summary/{requests.utils.quote(query)}"
        headers = {"User-Agent": "TegmenAI/1.0 (Educational Bot)"}
        w_res = requests.get(wiki_url, headers=headers, timeout=4)
        if w_res.status_code == 200:
            extract = w_res.json().get("extract")
            if extract:
                results.append(f"[WIKIPEDIA CANLI ÖZET]: {extract}")
    except Exception:
        pass

    # Katman B: DuckDuckGo Anlık Bilgi Endpoint'i
    try:
        ddg_url = f"https://api.duckduckgo.com/?q={requests.utils.quote(query)}&format=json&no_html=1&skip_disambig=1"
        d_res = requests.get(ddg_url, timeout=4).json()
        abstract = d_res.get("AbstractText", "")
        if abstract:
            results.append(f"[WEB BİLGİ MERKEZİ]: {abstract}")
        for item in d_res.get("RelatedTopics", [])[:2]:
            t = item.get("Text")
            if t:
                results.append(f"[EK BAĞLANTI]: {t}")
    except Exception:
        pass

    # Katman C: DuckDuckGo Standart Arama (Metin sonuçları)
    if not results:
        try:
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                ddg_list = list(ddgs.text(query, max_results=3))
                for r in ddg_list:
                    body = r.get("body")
                    if body:
                        results.append(f"[{r.get('title')}]: {body}")
        except Exception:
            pass

    return "\n\n".join(results)[:2500] if results else ""

# Üst Teknoloji Paneli
st.markdown(
    f"""
    <div class="tech-header">
        <div>
            <div class="tech-title">⚡ Tegmen's Jarvis CORE // v1.0</div>
            <div style="font-size: 12px; color: #7f97b5; margin-top: 4px;">MOTOR: {selected_model.upper()} | EVRENSEL AĞ AKTİF</div>
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
if prompt := st.chat_input("Sorgu, komut veya araştırma konusu girin..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="⚡"):
        with st.spinner("CANLI VERİ AKIŞI VE AĞ TARAMASI SAĞLANIYOR..."):
            extra_context = ""
            prompt_lower = prompt.lower()
            
            # Hava Durumu Telemetrisi (Dünyadaki her şehir için)
            if any(w in prompt_lower for w in ["hava", "derece", "sıcaklık", "yağmur", "weather"]):
                extra_context = get_live_weather(prompt)
            
            # Hava durumu değilse veya sonuç dönmediyse Genel İnternet Taraması
            if not extra_context:
                extra_context = search_general_web(prompt)

            system_instruction = (
                "Sen fütüristik, zeki, doğrudan ve yüksek analitik kabiliyete sahip Türkçe bir yapay zeka çekirdeğisin. "
                "Cevaplarını net, profesyonel, modern ve akıcı bir Türkçe ile sun. Gereksiz dolambaçlı laflar etme. "
                "Sana iletilen 'CANLI TELEMETRİ / VERİ' bilgilerini kesin gerçek kabul ederek kullanıcıyı anında bilgilendir. "
                "Kullanıcıya asla 'internete erişimim yok' deme; sağlanan canlı verileri ve genel bilgini harmanlayarak yanıtla."
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
                
                # Canlı veri geldiyse neon rozet göster
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
