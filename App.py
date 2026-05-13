import streamlit as st
import requests
import random

WG_APP_ID = "72581434ba12f4c4500d00618d0cdadf"

st.set_page_config(page_title="WoT Garage Game", layout="centered")

st.title("🎰 WoT Garage Web Game")

# ================= SESSION =================

if "garage" not in st.session_state:
    st.session_state.garage = []

if "stats" not in st.session_state:
    st.session_state.stats = {}

# ================= INPUT =================

player = st.text_input("Enter player nickname")

# ================= API =================

def get_account_id(name):
    url = f"https://api.worldoftanks.eu/wot/account/list/?application_id={WG_APP_ID}&search={name}"
    r = requests.get(url).json()
    data = r.get("data", [])
    return data[0]["account_id"] if data else None


def load_tanks(account_id):
    url = f"https://api.worldoftanks.eu/wot/account/tanks/?application_id={WG_APP_ID}&account_id={account_id}"
    r = requests.get(url).json()
    data = r.get("data", {}).get(str(account_id), [])
    return data


def load_stats(account_id):
    url = f"https://api.worldoftanks.eu/wot/tanks/stats/?application_id={WG_APP_ID}&account_id={account_id}"
    r = requests.get(url).json()
    data = r.get("data", {}).get(str(account_id), [])

    stats = {}

    for t in data:
        stats[t["tank_id"]] = {
            "battles": t["all"]["battles"],
            "wins": t["all"]["wins"],
            "damage": t["all"]["damage_dealt"]
        }

    return stats


def calc_stats(tank_id):
    s = st.session_state.stats.get(tank_id)

    if not s or s["battles"] == 0:
        return None

    wr = (s["wins"] / s["battles"]) * 100
    dmg = s["damage"] / s["battles"]

    return round(wr, 2), round(dmg), s["battles"]

# ================= LOAD PLAYER =================

if st.button("Load Player"):

    acc = get_account_id(player)

    if not acc:
        st.error("Player not found")
    else:
        raw = load_tanks(acc)
        st.session_state.stats = load_stats(acc)

        st.session_state.garage = raw

        st.success(f"Loaded {len(raw)} tanks")

# ================= FILTERS =================

garage = st.session_state.garage

if garage:

    nations = ["All"] + sorted(set(t["nation"] for t in garage))
    types = ["All"] + sorted(set(t["type"] for t in garage))
    tiers = ["All"] + sorted(set(str(t["tier"]) for t in garage))

    col1, col2, col3 = st.columns(3)

    nation = col1.selectbox("Nation", nations)
    ttype = col2.selectbox("Type", types)
    tier = col3.selectbox("Tier", tiers)

    def filtered():
        out = []
        for t in garage:
            if nation != "All" and t["nation"] != nation:
                continue
            if ttype != "All" and t["type"] != ttype:
                continue
            if tier != "All" and str(t["tier"]) != tier:
                continue
            out.append(t)
        return out

    # ================= SPIN =================

    if st.button("🎰 SPIN BATTLE"):

        pool = filtered()

        if not pool:
            st.warning("No tanks found")
        else:

            final = random.choice(pool)

            st.subheader(f"🎯 {final['name']}")

            stats = calc_stats(final["tank_id"])

            if stats:
                wr, dmg, battles = stats
                st.write(f"Winrate: {wr}%")
                st.write(f"Avg Damage: {dmg}")
                st.write(f"Battles: {battles}")
            else:
                st.write("No stats available")

# ================= EMPTY STATE =================

else:
    st.info("Enter player name and load data")
