import streamlit as st
import pandas as pd
import os
from datetime import datetime
from PIL import Image

# App title
st.set_page_config(page_title="สแน็ป สแน็ป", layout="wide")
st.title("📸 สแน็ป สแน็ป – IRL Pokédex")

# File paths
SAVE_DIR = "snap_data"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

# Predefined animal list (alphabetically sorted)
ANIMALS = sorted([
    "Alpaca", "Bat", "Buffalo", "Capybara", "Cat", "Chicken", "Cow", "Crab", "Crocodile",
    "Dabenniao (Malayan Night Heron)", "Deer", "Dog", "Donkey", "Duck", "Eagle", "Elephant",
    "Erawan (Three-Headed Elephant)", "Frog", "Gecko", "Goat", "Goose", "Hedgehog", "Heron", "Horse",
    "Hornbill", "Koi Fish", "Lizard", "Macaque", "Monkey", "Mosquito", "Mouse", "Naga (Serpent)",
    "Ostrich", "Owl", "Parrot", "Peacock", "Penguin", "Pig", "Pigeon", "Porcupine", "Rabbit",
    "Rat", "Raven", "Rooster", "Seagull", "Sheep", "Shrimp", "Snake", "Sparrow", "Squirrel",
    "Starling", "Swan", "Tiger", "Turtle", "Water Buffalo", "Yak", "Zebra"
])

# Helper function
def get_user_filepath(username):
    return os.path.join(SAVE_DIR, f"{username}_entries.csv")

# User login
st.sidebar.header("👤 User Login")
username = st.sidebar.text_input("Enter your name", value="Ash")

# Load or create user data
user_file = get_user_filepath(username)
if os.path.exists(user_file):
    df = pd.read_csv(user_file)
else:
    df = pd.DataFrame(columns=[
        "Animal", "Score", "Stars", "Tier", "Photo", "Latitude", "Longitude", "Location", "Timestamp"
    ])

# Main upload form
st.subheader("📤 Upload a New Photo")
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
            st.warning("Entry exists with equal or higher score. Not replacing.")
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
            df.to_csv(user_file, index=False)
            st.success("Saved!")

# Pokédex tab
st.subheader("📘 Your Pokédex")
for animal in ANIMALS:
    col = st.columns([1, 4])
    if animal in df["Animal"].values:
        col[0].markdown("✅")
        entry = df[df["Animal"] == animal].iloc[0]
        if col[1].button(f"{animal} - {entry['Score']} pts ({entry['Tier']})", key=animal):
            st.image(entry["Photo"], width=300, caption=f"{animal} ({entry['Stars']}⭐, {entry['Tier']})")
            st.markdown(f"📍 **Location:** {entry['Location']}  \n🌐 **Coords:** {entry['Latitude']}, {entry['Longitude']}  \n🕒 **Time:** {entry['Timestamp']}")
    else:
        col[0].markdown("⬜")
        col[1].markdown(animal)

# GPT Rater button
st.markdown("### 🤖 Rate your photos!")
st.markdown("[Launch Snap Snap Photo Rater](https://chatgpt.com/g/g-6892ce3fa6e48191bee880a53eed4a09-snap-snap-photo-rater)")

