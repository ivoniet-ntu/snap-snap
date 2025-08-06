import streamlit as st
import os
import json
from datetime import datetime
from PIL import Image

st.set_page_config(page_title="สแน็ป สแน็ป", layout="wide")

DATA_DIR = "snap_data"
os.makedirs(DATA_DIR, exist_ok=True)

animal_list = sorted([
    "Alpaca", "Bat", "Bear", "Bee", "Buffalo", "Butterfly", "Capybara", "Cat", "Chicken", "Cow",
    "Crab", "Crocodile", "Deer", "Dog", "Dolphin", "Duck", "Eagle", "Elephant", "Erawan",
    "Frog", "Gecko", "Goat", "Goldfish", "Horse", "Hornbill", "Iguana", "Jellyfish", "Koala",
    "Lizard", "Macaque", "Monkey", "Mosquito", "Mouse", "Octopus", "Ostrich", "Otter", "Owl",
    "Panda", "Parrot", "Peacock", "Penguin", "Pig", "Pigeon", "Rabbit", "Raccoon", "Rat",
    "Rooster", "Seagull", "Shark", "Sheep", "Snail", "Snake", "Spider", "Squirrel", "Tiger",
    "Turtle", "Whale", "Yak", "Zebra", "Dabenniao", "Naga"
])

# --- Utility Functions ---

def get_user_data_file(username):
    return os.path.join(DATA_DIR, f"{username}_pokedex.json")

def load_user_pokedex(username):
    filepath = get_user_data_file(username)
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    return {}

def save_user_pokedex(username, data):
    filepath = get_user_data_file(username)
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)

def get_medal(score):
    if score >= 4000:
        return "💎 Diamond"
    elif score >= 3500:
        return "🥇 Gold"
    elif score >= 2500:
        return "🥈 Silver"
    else:
        return "🥉 Bronze"

# --- App Interface ---

st.title("📸 สแน็ป สแน็ป")
st.markdown("A real-life Pokémon Snap experience. Rate your animal encounters!")

username = st.text_input("Enter your name", value="Player1")

menu = st.sidebar.radio("Menu", ["📷 New Entry", "📖 Pokédex"])

if menu == "📷 New Entry":
    st.header("New Animal Photo Entry")

    animal = st.selectbox("Select Animal", animal_list)
    uploaded_file = st.file_uploader("Upload Photo", type=["jpg", "jpeg", "png"])
    score = st.number_input("Enter Score", min_value=0, max_value=5000, value=3000, step=50)
    stars = st.selectbox("Star Rating (Behavior)", ["⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐"])
    location = st.text_input("Where did you see it? (e.g., Lumpini Park, Bangkok)")
    date_seen = st.date_input("When did you see it?", value=datetime.today())

    if st.button("Save Entry") and uploaded_file:
        pokedex = load_user_pokedex(username)
        new_entry = {
            "score": score,
            "stars": stars,
            "medal": get_medal(score),
            "location": location,
            "date": str(date_seen),
            "image": uploaded_file.getvalue()
        }

        # Update only if new score is higher
        if animal not in pokedex or score > pokedex[animal]["score"]:
            pokedex[animal] = new_entry
            save_user_pokedex(username, pokedex)
            st.success(f"Entry saved for {animal}!")
        else:
            st.warning("You already have a higher score for this animal.")

elif menu == "📖 Pokédex":
    st.header(f"Pokédex for {username}")
    pokedex = load_user_pokedex(username)

    for animal in animal_list:
        if animal in pokedex:
            entry = pokedex[animal]
            with st.expander(f"✅ {animal} - {entry['medal']} {entry['stars']}"):
                st.image(entry["image"], width=300)
                st.markdown(f"**Score**: {entry['score']}")
                st.markdown(f"**Location**: {entry['location']}")
                st.markdown(f"**Date**: {entry['date']}")
        else:
            st.markdown(f"🔲 {animal}")
