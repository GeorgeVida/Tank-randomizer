import customtkinter as ctk
import tkinter as tk
import requests
import random
from PIL import Image, ImageTk
import io

# ================= CONFIG =================

WG_APP_ID = "72581434ba12f4c4500d00618d0cdadf"

# ================= GLOBALS =================

xp = 0
level = 1

garage = []
favorites = []

tank_stats = {}
img_ref = None

# ================= LOAD ALL TANKS =================

def load_all_tanks():

    url = f"https://api.worldoftanks.eu/wot/encyclopedia/vehicles/?application_id={WG_APP_ID}"

    try:
        r = requests.get(url, timeout=10).json()
        data = r.get("data", {})

        tanks = {}

        for t in data.values():
            tanks[t["tank_id"]] = {
                "name": t.get("name"),
                "tier": str(t.get("tier")),
                "nation": t.get("nation"),
                "type": t.get("type"),
                "image": t.get("images", {}).get("big_icon"),
                "tank_id": t["tank_id"]
            }

        return tanks

    except:
        return {}


all_tanks = load_all_tanks()

# ================= STATS API =================

def load_tank_stats(account_id):

    url = (
        f"https://api.worldoftanks.eu/wot/tanks/stats/"
        f"?application_id={WG_APP_ID}&account_id={account_id}"
    )

    try:
        r = requests.get(url, timeout=10).json()
        data = r.get("data", {}).get(str(account_id), [])

        stats = {}

        for t in data:
            stats[t["tank_id"]] = {
                "battles": t["all"]["battles"],
                "wins": t["all"]["wins"],
                "damage": t["all"]["damage_dealt"]
            }

        return stats

    except:
        return {}

# ================= ACCOUNT SEARCH =================

def get_account_id(name):

    url = f"https://api.worldoftanks.eu/wot/account/list/?application_id={WG_APP_ID}&search={name}"

    try:
        r = requests.get(url, timeout=10).json()
        data = r.get("data", [])
        if not data:
            return None
        return data[0]["account_id"]
    except:
        return None


def load_player_tanks(account_id):

    url = f"https://api.worldoftanks.eu/wot/account/tanks/?application_id={WG_APP_ID}&account_id={account_id}"

    try:
        r = requests.get(url, timeout=10).json()
        data = r.get("data", {}).get(str(account_id), [])

        ids = [t["tank_id"] for t in data]

        return [all_tanks[i] for i in ids if i in all_tanks]

    except:
        return []

# ================= STATS HELPER =================

def get_stats(tank_id):

    s = tank_stats.get(tank_id)

    if not s or s["battles"] == 0:
        return None

    wr = (s["wins"] / s["battles"]) * 100
    dmg = s["damage"] / s["battles"]

    return {
        "wr": round(wr, 2),
        "dmg": round(dmg),
        "battles": s["battles"]
    }

# ================= PLAYER LOAD =================

def load_player():

    global garage, tank_stats

    name = player_var.get().strip()

    if not name:
        set_result("Enter player name")
        return

    set_result("Loading...")

    account_id = get_account_id(name)

    if not account_id:
        set_result("Player not found")
        return

    garage = load_player_tanks(account_id)
    tank_stats = load_tank_stats(account_id)

    update_filters()
    update_stats()

    set_result(f"Loaded {name} ({len(garage)} tanks)")

# ================= XP =================

def add_xp(amount=25):

    global xp, level

    xp += amount

    if xp >= level * 120:
        xp -= level * 120
        level += 1

    update_stats()

# ================= FILTER =================

def filtered():

    out = []

    for t in garage:

        if tier_var.get() != "All" and t["tier"] != tier_var.get():
            continue

        if nation_var.get() != "All" and t["nation"] != nation_var.get():
            continue

        if type_var.get() != "All" and t["type"] != type_var.get():
            continue

        out.append(t)

    return out

# ================= IMAGE =================

def load_image(url):

    global img_ref

    try:
        r = requests.get(url, timeout=5)
        img = Image.open(io.BytesIO(r.content))
        img = img.resize((420, 220), Image.LANCZOS)

        img_ref = ImageTk.PhotoImage(img)
        img_label.configure(image=img_ref)

    except:
        pass

# ================= SPIN =================

def spin():

    pool = filtered()

    if not pool:
        set_result("No tanks")
        return

    def step(i=0):

        if i < 20:

            t = random.choice(pool)
            set_result("🎲 " + t["name"])
            app.after(50, lambda: step(i + 1))

        else:

            final = random.choice(pool)

            s = get_stats(final["tank_id"])

            text = "🎯 " + final["name"]

            if s:
                text += f"\nWR:{s['wr']}% | DMG:{s['dmg']} | B:{s['battles']}"

            set_result(text)

            load_image(final["image"])

            if final["name"] not in favorites:
                favorites.append(final["name"])

    step()

# ================= UI =================

ctk.set_appearance_mode("dark")

app = ctk.CTk()
app.geometry("950x720")
app.title("WoT Garage Game")

player_var = ctk.StringVar()
tier_var = ctk.StringVar(value="All")
nation_var = ctk.StringVar(value="All")
type_var = ctk.StringVar(value="All")

img_label = tk.Label(app)
img_label.pack(pady=10)

def set_result(t):
    result.configure(text=t)

def update_stats():
    stats.configure(text=f"Level {level} | XP {xp}/{level*120} | Tanks {len(garage)}")

def update_filters():

    if not garage:
        return

    tiers = ["All"] + sorted(set(t["tier"] for t in garage))
    nations = ["All"] + sorted(set(t["nation"] for t in garage))
    types = ["All"] + sorted(set(t["type"] for t in garage))

    tier_menu.configure(values=tiers)
    nation_menu.configure(values=nations)
    type_menu.configure(values=types)

# ================= INPUT =================

frame = ctk.CTkFrame(app)
frame.pack(pady=10)

entry = ctk.CTkEntry(frame, textvariable=player_var, width=220)
entry.grid(row=0, column=0)

ctk.CTkButton(frame, text="LOAD", command=load_player).grid(row=0, column=1)

# ================= RESULT =================

result = ctk.CTkLabel(app, text="", font=("Arial", 22))
result.pack()

stats = ctk.CTkLabel(app, text="")
stats.pack()

# ================= FILTERS =================

filter_frame = ctk.CTkFrame(app)
filter_frame.pack(pady=10)

tier_menu = ctk.CTkOptionMenu(filter_frame, variable=tier_var, values=["All"])
tier_menu.grid(row=0, column=0)

nation_menu = ctk.CTkOptionMenu(filter_frame, variable=nation_var, values=["All"])
nation_menu.grid(row=0, column=1)

type_menu = ctk.CTkOptionMenu(filter_frame, variable=type_var, values=["All"])
type_menu.grid(row=0, column=2)

# ================= BUTTON =================

ctk.CTkButton(app, text="SPIN 🎰", command=spin).pack(pady=15)

# ================= START =================

app.mainloop()
