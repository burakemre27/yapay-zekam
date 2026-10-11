import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS

st.set_page_config(page_title="Gobels", page_icon="🌐")
st.title("Tegmen's Jarvis")

API_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=API_KEY)

# DuckDuckGo üzerinden canlı arama yapan fonksiyon
def search_web(query, max_results=3):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
            if not results:
                return ""
            search_snippets = []
            for r in results:
                search_snippets.append(f"Başlık: {r.get('title')}\nÖzet: {r.get('body')}")
            return "\n\n".join(search_snippets)
    except Exception:
        return ""

# En kararlı modeli tespit etme
PREFERRED_MODELS = [
    "llama-3.3-70b-versatile",
    "llama3-70b-8192",
    "llama-3.1-8b-instant",
    "llama3-8b-8192"
]

@st.cache_resource
def get_best_model():
    try:
        remote_models = [m.id for m in client.models.list().data]
        for pref in PREFERRED_MODELS:
            if pref in remote_models:
                return pref
        chat_models = [m for m in remote_models if "whisper" not in m and "allam" not in m.lower() and "guard" not in m]
        return chat_models[0] if chat_models else "llama-3.3-70b-versatile"
    except Exception:
        return "llama-3.3-70b-versatile"

active_model = get_best_model()

# Sohbet geçmişi
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Kullanıcı mesaj girdiğinde
if prompt := st.chat_input("Bir şeyler sorun (örneğin: Ankara hava durumu)..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("İnternette aranıyor ve yanıt hazırlanıyor..."):
            # Canlı web araması yap
            web_context = search_web(prompt)
            
            # Sistem talimatına arama sonuçlarını göm
            system_prompt = (
                "Sen internete canlı erişimi olan, zeki ve analitik bir Türkçe kişisel asistansın. "
                "Cevaplarını her zaman akıcı, açık ve profesyonel Türkçe ile ver. "
            )
            
            if web_context:
                system_prompt += (
                    f"\n\nAşağıda kullanıcının sorusuyla ilgili en güncel canlı internet arama sonuçları bulunmaktadır:\n"
                    f"--- İNTERNET VERİLERİ ---\n{web_context}\n----------------------\n"
                    "Bu güncel internet verilerini kullanarak kullanıcının sorusunu doğru ve eksiksiz yanıtla."
                )

            messages = [{"role": "system", "content": system_prompt}]
            for m in st.session_state.messages:
                messages.append({"role": m["role"], "content": m["content"]})

            completion = client.chat.completions.create(
                model=active_model,
                messages=messages,
            )
            response_text = completion.choices[0].message.content
            st.markdown(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text})
