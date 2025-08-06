import streamlit as st
import pandas as pd
import os
from datetime import datetime
from PIL import Image

# --- Setup ---
st.set_page_config(page_title="สแน็ป สแน็ป", layout="wide")
SAVE_DIR = "snap_data"
os.makedirs(SAVE_DIR, exist_ok=True)

# --- Animal List ---
ANIMALS = sorted([
    "Alpaca", "Bat", "Bear", "Bee", "Buffalo", "Butterfly", "Capybara", "Cat", "Chicken", "Cow",
    "Crab", "Crocodile", "Dabenniao", "Deer", "Dog", "Dolphin", "Dragonfly", "Duck", "Eagle", 
    "Elephant", "Erawan", "Frog", "Gecko", "Goat", "Goldfish", "Horse", "Hornbill", "Iguana", 
    "Jellyfish", "Koala", "Lizard", "Macaque", "Monkey", "Mosquito", "Mouse", "Naga", "Octopus", 
    "Ostrich", "Otter", "Owl", "Panda", "Parrot", "Peacock", "Penguin", "Pig", "Pigeon", "Rabbit", 
    "Raccoon", "Rat", "Rooster", "Seagull", "Shark", "Sheep", "Snail", "Snake", "Spider", 
    "Squirrel", "Tiger", "Tokay Gecko", "Turtle", "Water Monitor", "Whale", "Yak", "Zebra"
])

# --- Functions ---
def get_user_filepath(username):
    return os.path.join(SAVE_DIR, f"{username.lower()}_entries.csv")

def save_entry(df, user_file):
    df.to_csv(user_file, index=False)

# --- Sidebar Navigation ---
st.sidebar.header("👤 Player Login")
username = st.sidebar.text_input("Enter your name").strip()

if not username:
    st.warning("Please enter your name to continue.")
    st.stop()

user_file = get_user_filepath(username)
if os.path.exists(user_file):
    df = pd.read_csv(user_file)
else:
    df = pd.DataFrame(columns=[
        "Animal", "Score", "Stars", "Tier", "Photo", "Latitude", "Longitude", "Location", "Timestamp"
    ])

# Sidebar navigation
page = st.sidebar.radio("Navigate", ["📤 Upload", "📘 Pokédex", "🤖 Photo Rater"])

# --- Upload Page ---
if page == "📤 Upload":
    st.title("📸 สแน็ป สแน็ป – IRL Pokédex")
    st.subheader(f"Welcome, {username}!")

    with st.form("upload_form"):
        animal = st.selectbox("Which animal did you snap?", ANIMALS)
        score = st.number_input("Enter total score (0–6000)", min_value=0, max_value=6000, step=10)
        stars = st.selectbox("How many stars (pose)?", [1, 2, 3, 4])
        tier = st.selectbox("Medal rating", ["Bronze", "Silver", "Gold", "Diamond"])
        photo = st.file_uploader("Upload photo", type=["jpg", "jpeg", "png"])
        lat = st.text_input("Latitude", placeholder="Optional")
        lon = st.text_input("Longitude", placeholder="Optional")
        location_name = st.text_input("Location name", placeholder="e.g. Chatuchak Park")
        submit = st.form_submit_button("Save Entry")

        if submit and photo:
            photo_path = os.path.join(SAVE_DIR, f"{username}_{animal}_{datetime.now().isoformat()}.jpg")
            with open(photo_path, "wb") as f:
                f.write(photo.read())

            # Replace if better score exists
            existing = df[df["Animal"] == animal]
            if not existing.empty and score <= existing["Score"].max():
                st.warning("You already have a better or equal score for this animal.")
            else:
                df = df[df["Animal"] != animal]
                new_entry = pd.DataFrame([{
                    "Animal": animal,
                    "Score": score,
                    "Stars": stars,
                    "Tier": tier,
                    "Photo": photo_path,
                    "Latitude": lat,
                    "Longitude": lon,
                    "Location": location_name,
                    "Timestamp": datetime.now().isoformat()
                }])
                df = pd.concat([df, new_entry], ignore_index=True)
                save_entry(df, user_file)
                st.success("Saved!")

# --- Pokédex Page ---
elif page == "📘 Pokédex":
    st.title(f"📘 Pokédex – {username}")
    for animal in ANIMALS:
        col = st.columns([1, 4])
        if animal in df["Animal"].values:
            entry = df[df["Animal"] == animal].iloc[0]
            col[0].markdown("✅")
            if col[1].button(f"{animal} – {entry['Score']} pts ({entry['Tier']})", key=animal):
                st.image(entry["Photo"], width=300, caption=f"{animal} ({entry['Stars']}⭐, {entry['Tier']})")
                st.markdown(f"📍 **Location:** {entry['Location']}")
                st.markdown(f"🌐 **Coords:** {entry['Latitude']}, {entry['Longitude']}")
                st.markdown(f"🕒 **Time:** {entry['Timestamp']}")
        else:
            col[0].markdown("⬜")
            col[1].markdown(animal)

# --- GPT Photo Rater Page ---
elif page == "🤖 Photo Rater":
    st.title("🤖 Rate your photos!")
    st.markdown("Use the Snap Snap GPT to get a score suggestion:")
    st.markdown("[Launch Snap Snap Photo Rater](https://chatgpt.com/g/g-6892ce3fa6e48191bee880a53eed4a09-snap-snap-photo-rater)")
