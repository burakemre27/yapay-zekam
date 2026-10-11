import streamlit as st
from groq import Groq

st.set_page_config(page_title="Özel Yapay Zekam", page_icon="🤖")
st.title("🤖 Kendi Yapay Zeka Asistanım")

API_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=API_KEY)

# Aktif modeli otomatik tespit et (Hata almayı tamamen engeller)
@st.cache_resource
def get_available_model():
    try:
        models = client.models.list()
        # Aktif sohbet modellerinden ilkini al
        chat_models = [m.id for m in models.data if "whisper" not in m.id and "safetensors" not in m.id]
        return chat_models[0] if chat_models else "llama3-8b-8192"
    except Exception:
        return "llama3-8b-8192"

active_model = get_available_model()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Bir şeyler yazın..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    messages = [
        {"role": "system", "content": "Sen yardımsever, doğrudan cevap veren zeki bir kişisel asistansın."}
    ]
    for m in st.session_state.messages:
        messages.append({"role": m["role"], "content": m["content"]})

    with st.chat_message("assistant"):
        completion = client.chat.completions.create(
            model=active_model,
            messages=messages,
        )
        response_text = completion.choices[0].message.content
        st.markdown(response_text)
        st.session_state.messages.append({"role": "assistant", "content": response_text})
