import streamlit as st
import pandas as pd
import os
import pydeck as pdk
from datetime import datetime

# Title
st.set_page_config(page_title="Snap Snap IRL", layout="wide")
st.title("📷 สแน็ป สแน็ป – Real Life Pokémon Snap")

DATA_FILE = "snap_log.csv"

# Starter animal list (60, alphabetical)
animal_list = sorted([
    "Alpaca", "Ant", "Bat", "Bear", "Bee", "Beetle", "Bison", "Butterfly", "Capybara", "Cat",
    "Chicken", "Cicada", "Cobra", "Crocodile", "Dabenniao (Malayan Night Heron)", "Deer", "Dog", "Dolphin",
    "Dragonfly", "Duck", "Eagle", "Erawan (3-headed Elephant)", "Elephant", "Frog", "Gecko", "Giraffe",
    "Goat", "Hedgehog", "Hornbill", "Horse", "Iguana", "Koala", "Leopard", "Lizard", "Macaw", "Macaque",
    "Monkey", "Mosquito", "Mouse", "Naga (Thai Dragon)", "Ostrich", "Owl", "Panda", "Parrot", "Peacock",
    "Penguin", "Pig", "Pigeon", "Rabbit", "Rhinoceros", "Scorpion", "Shark", "Snake", "Spider", "Squirrel",
    "Tiger", "Turtle", "Yak (Temple Guardian)", "Zebra"
])

# Load or create data
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    df = pd.DataFrame(columns=["Name", "Animal", "Photo", "Pose", "Size", "Direction", "Placement", "Other", "Total", "Place", "Lat", "Lon", "Timestamp"])
    df.to_csv(DATA_FILE, index=False)

# Sidebar navigation
page = st.sidebar.radio("Navigation", ["Add Entry", "Pokédex", "Map", "Delete Entry"])

# Add Entry
if page == "Add Entry":
    st.header("📸 Add a New Photo Entry")
    with st.form("entry_form"):
        name = st.text_input("Your Name")
        animal = st.selectbox("Animal", animal_list)
        photo = st.file_uploader("Upload Photo (optional)", type=["jpg", "png", "jpeg"])
        col1, col2, col3 = st.columns(3)
        with col1:
            pose = st.slider("Pose", 0, 1000, 500)
            size = st.slider("Size", 0, 1000, 500)
        with col2:
            direction = st.slider("Direction", 0, 1000, 500)
            placement = st.slider("Placement", 0, 1000, 500)
        with col3:
            other = st.slider("Other", 0, 1000, 500)
            place = st.text_input("Place name (e.g. Lumphini Park)")
            lat = st.number_input("Latitude", format="%.6f")
            lon = st.number_input("Longitude", format="%.6f")

        submitted = st.form_submit_button("Save Entry")

    if submitted:
        if not name or not animal:
            st.warning("Please enter your name and select an animal.")
        else:
            total = pose + size + direction + placement + other
            timestamp = datetime.now().isoformat()
            new_row = {
                "Name": name, "Animal": animal, "Photo": photo.name if photo else "",
                "Pose": pose, "Size": size, "Direction": direction, "Placement": placement,
                "Other": other, "Total": total, "Place": place, "Lat": lat, "Lon": lon,
                "Timestamp": timestamp
            }

            # Check for existing better score for same name/animal
            match = (df["Name"] == name) & (df["Animal"] == animal)
            if match.any():
                if total > df.loc[match, "Total"].max():
                    df = df[~match]
                    df.loc[len(df)] = new_row
                    st.success(f"✅ Updated! Higher score: {total}")
                else:
                    st.info("📉 You already have a higher-scoring entry. Not saved.")
            else:
                df.loc[len(df)] = new_row
                st.success(f"✅ Saved with total score: {total}")

            df.to_csv(DATA_FILE, index=False)

# Pokédex
elif page == "Pokédex":
    st.header("📖 Pokédex")

    user_filter = st.selectbox("Choose Player", ["All Users"] + sorted(df["Name"].unique()))

    filtered_df = df if user_filter == "All Users" else df[df["Name"] == user_filter]

    seen = filtered_df["Animal"].unique()

    for animal in animal_list:
        if animal in seen:
            best_entry = filtered_df[filtered_df["Animal"] == animal].sort_values("Total", ascending=False).iloc[0]
            st.markdown(f"✅ **{animal}** – {best_entry['Total']} pts ({best_entry['Name']})")
        else:
            st.markdown(f"🔲 {animal}")

# Map
elif page == "Map":
    st.header("🗺️ Snap Map")

    if len(df) == 0:
        st.info("No entries with location yet.")
    else:
        mappable_df = df.dropna(subset=["Lat", "Lon"])
        if len(mappable_df) == 0:
            st.info("No location data available.")
        else:
            st.dataframe(mappable_df[["Name", "Animal", "Place", "Lat", "Lon"]])

            st.pydeck_chart(pdk.Deck(
                map_style="mapbox://styles/mapbox/streets-v12",
                initial_view_state=pdk.ViewState(
                    latitude=mappable_df["Lat"].mean(),
                    longitude=mappable_df["Lon"].mean(),
                    zoom=6,
                    pitch=0,
                ),
                layers=[
                    pdk.Layer(
                        "ScatterplotLayer",
                        data=mappable_df,
                        get_position='[Lon, Lat]',
                        get_color='[200, 30, 0, 160]',
                        get_radius=30000,
                        pickable=True
                    )
                ],
                tooltip={"text": "{Name} saw {Animal} at {Place}"}
            ))

# Delete
elif page == "Delete Entry":
    st.header("🗑️ Delete an Entry")
    if df.empty:
        st.info("No entries to delete.")
    else:
        name = st.selectbox("Your Name", sorted(df["Name"].unique()))
        animal = st.selectbox("Animal", sorted(df[df["Name"] == name]["Animal"].unique()))
        delete = st.button("Delete Entry")
        if delete:
            df = df[~((df["Name"] == name) & (df["Animal"] == animal))]
            df.to_csv(DATA_FILE, index=False)
            st.success(f"Deleted {animal} entry for {name}.")
