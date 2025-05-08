import streamlit as st
import math

st.title("🧱 Shower Tile Layout Calculator")

st.markdown("Enter your wall and tile dimensions to calculate how many tiles and boxes you'll need for a shower tiling project.")

# Inputs
st.header("Wall Dimensions")
wall_height = st.number_input("Wall Height (inches)", min_value=1, value=84)
wall_width = st.number_input("Wall Width (inches)", min_value=1, value=36)

st.header("Tile Dimensions")
tile_height = st.number_input("Tile Height (inches)", min_value=1, value=12)
tile_width = st.number_input("Tile Width (inches)", min_value=1, value=12)

st.header("Tile Packaging")
tiles_per_box = st.number_input("Tiles per Box", min_value=1, value=10)
waste_percentage = st.slider("Waste Buffer (%)", min_value=0, max_value=50, value=10)

# Calculations
tiles_high = math.ceil(wall_height / tile_height)
tiles_wide = math.ceil(wall_width / tile_width)
total_tiles = tiles_high * tiles_wide

total_tiles_with_waste = math.ceil(total_tiles * (1 + waste_percentage / 100))
boxes_needed = math.ceil(total_tiles_with_waste / tiles_per_box)

# Outputs
st.header("Results")
st.write(f"**Tiles High:** {tiles_high}")
st.write(f"**Tiles Wide:** {tiles_wide}")
st.write(f"**Total Tiles Needed (no waste):** {total_tiles}")
st.write(f"**Total Tiles Needed (with {waste_percentage}% waste):** {total_tiles_with_waste}")
st.write(f"**Boxes Needed:** {boxes_needed}")

# Optional Layout Grid (simple text)
st.subheader("Tile Layout Grid Preview")
layout_preview = "\n".join([" ".join(["🧱" for _ in range(tiles_wide)]) for _ in range(min(10, tiles_high))])
st.text(layout_preview)

st.caption("Note: Preview shows max 10 rows to keep it readable.")
