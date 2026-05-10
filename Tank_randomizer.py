
import streamlit as st
import requests
import random
import json
import os

API_KEY = "TO_API_KEY"
BASE = "https://api.worldoftanks.eu/wot"

HISTORY_FILE = "history.json"
FAV_FILE = "favorites.json"


# ---------------- STORAGE ----------------

def load(file):
    if not os.path.exists(file):
        return []
    with open(file, "r") as f:
        return json.load(f)

def save(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)


# ---------------- API ----------------

def get_account_id(name):
    r = requests.get(f"{BASE}/account/list/", params={
        "application_id": API_KEY,
        "search": name,
        "limit": 1
    }).json()

    return r["data"][0]["account_id"] if r["data"] else None


def get_tanks(account_id):
    r = requests.get(f"{BASE}/account/tanks/", params={
        "application_id": API_KEY,
        "account_id": account_id
    }).json()

    return r["data"].get(str(account_id), [])


def get_tank_info(tank_id):
    r = requests.get(f"{BASE}/encyclopedia/vehicles/", params={
        "application_id": API_KEY,
        "tank_id": tank_id
    }).json()

    return r["data"].get(str(tank_id))


# ---------------- LOGIC ----------------

def winrate(stats):
    b = stats["battles"]
    return (stats["wins"] / b * 100) if b else 0


def avg_damage(stats):
    b = stats["battles"]
    return stats["damage_dealt"] // b if b else 0


# ---------------- UI ----------------

st.set_page_config(page_title="Tank Randomiser", layout="wide")

st.title("🎲 Tank Randomiser")


player = st.text_input("Player name")
min_tier = st.selectbox("Min tier", [None, 5, 6, 7, 8, 9, 10])

roll = st.button("🎰 Roll tank")


# session state
if "history" not in st.session_state:
    st.session_state.history = load(HISTORY_FILE)

if "favorites" not in st.session_state:
    st.session_state.favorites = load(FAV_FILE)


# ---------------- MAIN ----------------

if player:

    account_id = get_account_id(player)

    if not account_id:
        st.error("Player not found")
        st.stop()

    tanks = get_tanks(account_id)

    if min_tier:
        tanks = [t for t in tanks if t.get("tier", 0) >= min_tier]


    if roll and tanks:

        # avoid repeats
        recent = [t["tank_id"] for t in st.session_state.history[-5:]]
        pool = [t for t in tanks if t["tank_id"] not in recent] or tanks

        chosen = random.choice(pool)
        tank_id = chosen["tank_id"]

        info = get_tank_info(tank_id)
        stats = chosen["statistics"]

        wr = winrate(stats)
        dmg = avg_damage(stats)

        # save history
        st.session_state.history.append(chosen)
        save(HISTORY_FILE, st.session_state.history)


        # ---------------- DISPLAY ----------------

        col1, col2 = st.columns([1, 2])

        with col1:
            st.image(info["images"]["big_icon"], width=250)

        with col2:
            st.subheader(info["name"])

            c1, c2, c3 = st.columns(3)
            c1.metric("Battles", stats["battles"])
            c2.metric("WR %", round(wr, 2))
            c3.metric("Avg dmg", dmg)

            # buttons
            if st.button("⭐ Add to favorites"):
                st.session_state.favorites.append(chosen)
                save(FAV_FILE, st.session_state.favorites)

            if st.button("🔁 Roll again"):
                st.rerun()


# ---------------- SIDEBAR ----------------

st.sidebar.title("📊 Data")

st.sidebar.subheader("⭐ Favorites")

for f in st.session_state.favorites[-10:]:
    st.sidebar.write(f"Tank ID: {f['tank_id']}")

st.sidebar.subheader("🕘 History")
