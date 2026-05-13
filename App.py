import streamlit as st
import requests
import random

WG_APP_ID = "72581434ba12f4c4500d00618d0cdadf"

st.title("🎰 WoT Garage Web App")

player = st.text_input("Enter player name")

if "garage" not in st.session_state:
    st.session_state.garage = []

def get_account_id(name):
    url = f"https://api.worldoftanks.eu/wot/account/list/?application_id={WG_APP_ID}&search={name}"
    r = requests.get(url).json()
    data = r.get("data", [])
    if not data:
        return None
    return data[0]["account_id"]

def load_tanks(account_id):
    url = f"https://api.worldoftanks.eu/wot/account/tanks/?application_id={WG_APP_ID}&account_id={account_id}"
    r = requests.get(url).json()
    data = r.get("data", {}).get(str(account_id), [])
    return [t["tank_id"] for t in data]

if st.button("Load Player"):

    acc = get_account_id(player)

    if not acc:
        st.error("Player not found")
    else:
        tanks = load_tanks(acc)
        st.session_state.garage = tanks
        st.success(f"Loaded {len(tanks)} tanks")

st.subheader("Garage")

if st.session_state.garage:
    st.write(st.session_state.garage)
else:
    st.write("No data")
