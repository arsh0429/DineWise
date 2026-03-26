"""DineWise - Premium Restaurant Reservation Assistant"""
import streamlit as st
from agent.orchestrator import Orchestrator

st.set_page_config(
    page_title="DineWise | Restaurant Reservations",
    page_icon="🍽️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Load premium CSS
with open("frontend/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Gradient header
st.markdown("""
<div class="header">
    <h1 class="logo">🍽️ DineWise</h1>
    <p class="tagline">Your personal restaurant concierge in Bangalore</p>
</div>
""", unsafe_allow_html=True)

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "orchestrator" not in st.session_state:
    st.session_state.orchestrator = None  # Lazy load - don't block page render

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🧑" if msg["role"] == "user" else "🍽️"):
        st.markdown(msg["content"])

# Chat input
if user_input := st.chat_input("Find restaurants, make reservations, or ask for recommendations..."):
    # Show user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(user_input)
    
    # Lazy-load orchestrator on first message
    with st.chat_message("assistant", avatar="🍽️"):
        if st.session_state.orchestrator is None:
            with st.spinner("🚀 Starting up DineWise agent (first time only)..."):
                try:
                    st.session_state.orchestrator = Orchestrator()
                except Exception as e:
                    st.markdown(f"⚠️ Failed to start agent: {e}")
                    st.stop()
        
        with st.spinner("Finding the best options for you..."):
            try:
                history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[:-1]]
                response = st.session_state.orchestrator.process_message(user_input, history)
            except Exception as e:
                response = f"⚠️ Error: {e}"
        st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})

# Sidebar
with st.sidebar:
    st.markdown("""
    <div class="sidebar-content">
        <h3>🍽️ DineWise</h3>
        <p>Premium dining reservations in Bangalore</p>
        <hr>
        <h4>📍 Neighborhoods</h4>
        <p>Koramangala • Indiranagar • Whitefield<br>
        HSR Layout • MG Road • Jayanagar<br>
        JP Nagar • Malleshwaram</p>
        <hr>
        <h4>💬 Try asking:</h4>
        <ul>
            <li>"Find Italian restaurants in Koramangala"</li>
            <li>"Recommend a place for a date night"</li>
            <li>"Book a table for 4 tomorrow at 7:30 PM"</li>
            <li>"Cancel my reservation DW-2026-ABC123"</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
