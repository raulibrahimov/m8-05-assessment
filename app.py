"""Streamlit chat UI for the Code Explainer micro-service.

Run with:

    pip install -r requirements.txt
    cp .env.example .env   # then fill in GEMINI_API_KEY
    streamlit run app.py
"""

import streamlit as st

from llm_service import ChatService

st.set_page_config(page_title="CodeExplainer", page_icon="🧑‍💻")
st.title("🧑‍💻 CodeExplainer")
st.caption("Paste a code snippet and I'll walk you through it.")

with st.sidebar:
    st.header("Settings")
    temperature = st.slider("Temperature", 0.0, 1.5, 0.3, 0.1)
    if st.button("Clear chat"):
        st.session_state.pop("service", None)
        st.session_state.pop("messages", None)
        st.rerun()

if "service" not in st.session_state:
    try:
        st.session_state.service = ChatService(temperature=temperature)
    except RuntimeError as e:
        st.error(str(e))
        st.stop()
if "messages" not in st.session_state:
    st.session_state.messages = []

service: ChatService = st.session_state.service
service.temperature = temperature

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Paste code or ask a question…"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        reply = st.write_stream(service.stream(prompt))

    st.session_state.messages.append({"role": "assistant", "content": reply})

with st.sidebar:
    st.caption(
        f"Tokens — in: {service.total_input_tokens} / "
        f"out: {service.total_output_tokens}"
    )
    st.caption(f"Model: `{service.model}`")
