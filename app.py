import streamlit as st
from groq import Groq

st.set_page_config(page_title="Özel Yapay Zekam", page_icon="🤖")
st.title("🤖 Kendi Yapay Zeka Asistanım")

API_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=API_KEY)

# Çok dilli ve kararlı çalışan ana modelleri sırayla dener
PREFERRED_MODELS = [
    "llama-3.3-70b-versatile",
    "llama3-70b-8192",
    "llama-3.1-8b-instant",
    "llama3-8b-8192",
    "mixtral-8x7b-32768"
]

@st.cache_resource
def get_best_model():
    try:
        remote_models = [m.id for m in client.models.list().data]
        for pref in PREFERRED_MODELS:
            if pref in remote_models:
                return pref
        # Listenin başındaki modellerden Arapça/özel varyant olmayan birini seç
        chat_models = [m for m in remote_models if "whisper" not in m and "allam" not in m.lower() and "guard" not in m]
        return chat_models[0] if chat_models else "llama-3.3-70b-versatile"
    except Exception:
        return "llama-3.3-70b-versatile"

active_model = get_best_model()

if "messages" not in st.session_state:
    st.session_state.messages = []

# Önceki mesajları göster
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Yeni mesaj girildiğinde
if prompt := st.chat_input("Bir şeyler yazın..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Sistem talimatında dili kesin olarak Türkçe'ye sabitle
    messages = [
        {
            "role": "system",
            "content": (
                "Sen yardımsever, akıllı ve analitik bir kişisel asistansın. "
                "Kullanıcıya daima akıcı, net ve düzgün bir Türkçe ile yanıt vereceksin. "
                "Kullanıcı başka bir dilde yazmasını açıkça istemediği sürece asla Arapça veya başka bir dil kullanma."
            ),
        }
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
