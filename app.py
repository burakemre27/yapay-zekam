import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS

st.set_page_config(page_title="Tegmen YILMAZ", page_icon="🌐")
st.title("🌐 Tegmen's Jarvis")

API_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=API_KEY)

# Hesabınızdaki aktif sohbet modellerini listele
@st.cache_data(ttl=3600)
def get_available_chat_models():
    try:
        model_list = client.models.list()
        # Ses (whisper) ve embedding modellerini filtrele
        valid_models = [
            m.id for m in model_list.data 
            if not any(x in m.id.lower() for x in ["whisper", "embed", "guard", "safetensors"])
        ]
        return valid_models if valid_models else ["llama-3.3-70b-versatile"]
    except Exception:
        return ["llama-3.3-70b-versatile"]

available_models = get_available_chat_models()
selected_model = st.sidebar.selectbox("Kullanılan Model", available_models, index=0)

# Web arama fonksiyonu
def search_web(query, max_results=3):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
            if not results:
                return ""
            snippets = []
            for r in results:
                title = str(r.get("title", "")).strip()
                body = str(r.get("body", "")).strip()
                if body:
                    snippets.append(f"{title}: {body}")
            full_text = "\n".join(snippets)
            return full_text[:2000]
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
        with st.spinner("Bilgiler taranıyor ve yanıt hazırlanıyor..."):
            web_info = search_web(prompt)

            system_instruction = (
                "Sen Türkçe konuşan, yardımsever ve zeki bir asistansın. "
                "Cevaplarını her zaman akıcı ve düzgün bir Türkçe ile ver."
            )
            
            if web_info:
                system_instruction += (
                    f"\n\nİnternetten alınan güncel bilgiler:\n{web_info}\n\n"
                    "Bu bilgileri kullanarak kullanıcının sorusunu net bir şekilde yanıtla."
                )

            payload = [{"role": "system", "content": system_instruction}]
            for m in st.session_state.messages[-6:]:
                payload.append({"role": m["role"], "content": m["content"]})

            try:
                completion = client.chat.completions.create(
                    model=selected_model,
                    messages=payload,
                    temperature=0.6,
                )
                response_text = completion.choices[0].message.content
                st.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})
            except Exception as e:
                st.error(f"Bağlantı hatası: {str(e)}")
