import streamlit as st

# Load your backend functions
from backend import ask  # Adjust to match your function

# Page config
st.set_page_config(page_title="ScoutBot", page_icon="🧢", layout="centered")

# Title
st.markdown("<h1 style='text-align: center;'>⚾ ScoutBot</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Ask me about baseball scouting reports (2013–2019)</p>", unsafe_allow_html=True)
st.markdown("---")

# Chat history (Session State)
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Ask me anything about a player..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = ask(prompt)  # Call your function
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
