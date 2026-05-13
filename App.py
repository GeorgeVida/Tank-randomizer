import streamlit as st

st.title("🎰 WoT Garage Game")

name = st.text_input("Player name")

if st.button("Load"):
    st.success(f"Hello {name}")
