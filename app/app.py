import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches

st.set_page_config(layout="wide")
st.title("🧱 Custom Shower Tile Layout Visualizer")

st.markdown("Enter wall and tile dimensions to visualize your tiling layout with accurate measurements.")

# --- Input section ---
col1, col2 = st.columns(2)
with col1:
    wall_width = st.number_input("Wall Width (in)", min_value=10, value=60)
    wall_height = st.number_input("Wall Height (in)", min_value=10, value=90)
    cutout_x = st.number_input("Cutout X Position (in)", min_value=0, value=40)
    cutout_y = st.number_input("Cutout Y Position (in)", min_value=0, value=0)
    cutout_width = st.number_input("Cutout Width (in)", min_value=0, value=20)
    cutout_height = st.number_input("Cutout Height (in)", min_value=0, value=20)

with col2:
    tile_width = st.number_input("Tile Width (in)", min_value=1, value=10)
    tile_height = st.number_input("Tile Height (in)", min_value=1, value=10)
    show_grid = st.checkbox("Show Grid", value=True)
    show_measurements = st.checkbox("Show Measurements", value=True)

# --- Plotting ---
fig, ax = plt.subplots(figsize=(8, 10))
ax.set_xlim(0, wall_width)
ax.set_ylim(0, wall_height)
ax.set_aspect('equal')
ax.set_xticks(range(0, wall_width + 1, 10))
ax.set_yticks(range(0, wall_height + 1, 10))
if show_grid:
    ax.grid(True, which='both', color='lightgrey', linewidth=0.5)

# Draw tiles
tiles_across = wall_width // tile_width
tiles_up = wall_height // tile_height
for i in range(int(tiles_across)):
    for j in range(int(tiles_up)):
        tile_x = i * tile_width
        tile_y = j * tile_height
        # Skip tiles in cutout
        if cutout_x < tile_x + tile_width and tile_x < cutout_x + cutout_width and \
           cutout_y < tile_y + tile_height and tile_y < cutout_y + cutout_height:
            continue
        rect = patches.Rectangle((tile_x, tile_y), tile_width, tile_height, linewidth=0.5, edgecolor='gray', facecolor='lightgray')
        ax.add_patch(rect)

# Draw wall outline
ax.add_patch(patches.Rectangle((0, 0), wall_width, wall_height, fill=False, edgecolor='black', linewidth=2))

# Draw cutout
if cutout_width > 0 and cutout_height > 0:
    ax.add_patch(patches.Rectangle((cutout_x, cutout_y), cutout_width, cutout_height, fill=True, color='white', edgecolor='black'))

# Draw measurement text
if show_measurements:
    ax.text(wall_width/2, wall_height + 2, f"{wall_width}\"", ha='center', color='blue')
    ax.text(-3, wall_height/2, f"{wall_height}\"", va='center', rotation=90, color='blue')
    if cutout_width > 0 and cutout_height > 0:
        ax.text(cutout_x + cutout_width/2, cutout_y - 5, f"{cutout_width}\"", ha='center', color='blue')
        ax.text(cutout_x - 3, cutout_y + cutout_height/2, f"{cutout_height}\"", va='center', rotation=90, color='blue')

ax.invert_yaxis()
st.pyplot(fig)

# --- Tile Count Summary ---
total_tiles = int(tiles_across * tiles_up)
st.subheader("Tile Count Estimate")
st.write(f"Tiles across: {int(tiles_across)}")
st.write(f"Tiles up: {int(tiles_up)}")
st.write(f"**Estimated usable tiles (not in cutout):** {total_tiles}")
