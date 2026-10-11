import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="Gobels", page_icon="🤖")
st.title("🤖 Tegmen YILMAZ Ai")

# Anahtarı Streamlit Secrets'tan güvenli oku
API_KEY = st.secrets["GEMINI_API_KEY"]

if "messages" not in st.session_state:
    st.session_state.messages = []

# Önceki mesajları ekranda listele
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Yeni mesaj girildiğinde
if prompt := st.chat_input("Bir şeyler yazın..."):
    # 1. Kullanıcı mesajını kaydet ve göster
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Mesaj geçmişini hazırla
    contents = [
        types.Content(
            role="model" if m["role"] == "assistant" else "user",
            parts=[types.Part.from_text(text=m["content"])],
        )
        for m in st.session_state.messages
    ]

    # 3. Yanıtı al ve göster
    with st.chat_message("assistant"):
        client = genai.Client(api_key=API_KEY)
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction="Sen yardımsever, doğrudan cevap veren analitik bir kişisel asistansın."
            ),
        )
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
