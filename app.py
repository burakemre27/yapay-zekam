import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS

st.set_page_config(page_title="TEGMEN", page_icon="🌐")
st.title("🌐 Tegmen's Jarvis")

API_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=API_KEY)

# Web arama fonksiyonu (Güvenli ve temizlenmiş metin)
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
            # Aşırı uzun metinleri sınırla
            full_text = "\n".join(snippets)
            return full_text[:2000]
    except Exception:
        return ""

if "messages" not in st.session_state:
    st.session_state.messages = []

# Önceki sohbeti göster
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Yeni mesaj geldiğinde
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

            # API'ye gidecek mesaj listesi
            payload = [{"role": "system", "content": system_instruction}]
            
            # Son 6 mesajı al (geçmişin çok uzayıp hata vermesini önler)
            for m in st.session_state.messages[-6:]:
                payload.append({"role": m["role"], "content": m["content"]})

            try:
                completion = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=payload,
                    temperature=0.6,
                )
                response_text = completion.choices[0].message.content
                st.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})
            except Exception as e:
                hata_mesaji = f"Bağlantı hatası oluştu: {str(e)}"
                st.error(hata_mesaji)
