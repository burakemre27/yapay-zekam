import streamlit as st
import httpx
from google import genai
from google.genai import types

st.set_page_config(page_title="Tegmen", page_icon="🤖")
st.title("🤖 Tegmen YILMAZZ Ai")

# Anahtarı secrets üzerinden al
API_KEY = st.secrets["GEMINI_API_KEY"]

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Bir şeyler yazın..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    contents = [
        types.Content(
            role="model" if m["role"] == "assistant" else "user",
            parts=[types.Part.from_text(text=m["content"])],
        )
        for m in st.session_state.messages
    ]

    with st.chat_message("assistant"):
        custom_http_client = httpx.Client(verify=False)
        client = genai.Client(
            api_key=API_KEY,
            http_options=types.HttpOptions(httpx_client=custom_http_client)
        )

        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction="Sen yardımsever, doğrudan cevap veren analitik bir kişisel asistansın."
            ),
        )
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
