import streamlit as st
from groq import Groq

st.set_page_config(page_title="Özel Yapay Zekam", page_icon="🤖")
st.title("🤖 Kendi Yapay Zeka Asistanım")

# Anahtarı Streamlit Secrets üzerinden al
API_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=API_KEY)

# Sohbet geçmişini başlat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Önceki mesajları ekranda göster
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Yeni mesaj girildiğinde
if prompt := st.chat_input("Bir şeyler yazın..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Modele gidecek mesaj listesi
    messages = [
        {"role": "system", "content": "Sen yardımsever, doğrudan cevap veren analitik ve zeki bir kişisel asistansın."}
    ]
    for m in st.session_state.messages:
        messages.append({"role": m["role"], "content": m["content"]})

    # Güncel ve stabil modelle yanıt üret
    with st.chat_message("assistant"):
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
        )
        response_text = completion.choices[0].message.content
        st.markdown(response_text)
        st.session_state.messages.append({"role": "assistant", "content": response_text})
