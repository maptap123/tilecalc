import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math

st.set_page_config(layout="wide")
st.title("🧱 Custom Shower Tile Layout Visualizer with Cut Tile Tracking")

st.markdown("Enter wall and tile dimensions to visualize your tiling layout, including cut tiles and accurate measurements.")

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
fig_width = wall_width / 10
fig_height = wall_height / 10
fig, ax = plt.subplots(figsize=(fig_width, fig_height))
ax.set_xlim(0, wall_width)
ax.set_ylim(0, wall_height)
ax.set_aspect('equal')
ax.set_xticks(range(0, wall_width + 1, 10))
ax.set_yticks(range(0, wall_height + 1, 10))
if show_grid:
    ax.grid(True, which='both', color='lightgrey', linewidth=0.5)

# Tiling calculation
tiles_across = math.ceil(wall_width / tile_width)
tiles_up = math.ceil(wall_height / tile_height)

full_tiles = 0
cut_tiles = 0

# Draw tiles
for i in range(tiles_across):
    for j in range(tiles_up):
        tile_x = i * tile_width
        tile_y = j * tile_height
        
        tile_right = tile_x + tile_width
        tile_top = tile_y + tile_height

        # Check if tile is in cutout
        in_cutout = cutout_x < tile_right and tile_x < cutout_x + cutout_width and \
                    cutout_y < tile_top and tile_y < cutout_y + cutout_height
        if in_cutout:
            continue

        # Determine tile size within bounds
        draw_width = min(tile_width, wall_width - tile_x)
        draw_height = min(tile_height, wall_height - tile_y)

        is_cut = draw_width < tile_width or draw_height < tile_height

        color = 'lightgray'
        edgecolor = 'red' if is_cut else 'gray'
        linewidth = 1 if is_cut else 0.5

        rect = patches.Rectangle((tile_x, tile_y), draw_width, draw_height,
                                 linewidth=linewidth, edgecolor=edgecolor, facecolor=color)
        ax.add_patch(rect)

        if is_cut:
            cut_tiles += 1
        else:
            full_tiles += 1

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
st.subheader("Tile Count Summary")
st.write(f"**Full Tiles:** {full_tiles}")
st.write(f"**Cut Tiles:** {cut_tiles}")
st.write(f"**Total Tiles Required:** {full_tiles + cut_tiles}")
