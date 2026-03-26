"""Minimal test - no CSS, no orchestrator. Just chat input."""
import streamlit as st

st.set_page_config(page_title="Test Chat", page_icon="🍽️")

st.title("🍽️ DineWise Test")
st.write("If you can see a text box below, type something and press Enter.")

if "msgs" not in st.session_state:
    st.session_state.msgs = []

for m in st.session_state.msgs:
    with st.chat_message(m["role"]):
        st.write(m["content"])

if prompt := st.chat_input("Type here..."):
    st.session_state.msgs.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    with st.chat_message("assistant"):
        st.write(f"You said: {prompt}")
    st.session_state.msgs.append({"role": "assistant", "content": f"You said: {prompt}"})
