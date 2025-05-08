import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math

st.set_page_config(layout="wide")
st.title("🧱 Custom Shower Tile Layout Visualizer with Multiple Cutouts")

st.markdown("Enter wall and tile dimensions to visualize your tiling layout, including cut tiles and accurate measurements.")

# --- Unit selection ---
unit = st.radio("Select unit:", ["inches", "feet"])
unit_factor = 12 if unit == "feet" else 1

# --- Input section ---
col1, col2 = st.columns(2)
with col1:
    wall_width = st.number_input(f"Wall Width ({unit})", min_value=1.0, value=60.0) * unit_factor
    wall_height = st.number_input(f"Wall Height ({unit})", min_value=1.0, value=90.0) * unit_factor

with col2:
    tile_width = st.number_input(f"Tile Width ({unit})", min_value=1.0, value=10.0) * unit_factor
    tile_height = st.number_input(f"Tile Height ({unit})", min_value=1.0, value=10.0) * unit_factor
    show_grid = st.checkbox("Show Grid", value=True)
    show_measurements = st.checkbox("Show Measurements", value=True)

# --- Multiple Cutouts ---
st.subheader("Cutouts")
num_cutouts = st.number_input("Number of Cutouts", min_value=0, max_value=5, value=1)
cutouts = []
for i in range(int(num_cutouts)):
    st.markdown(f"**Cutout {i+1}**")
    cx = st.number_input(f"Cutout {i+1} X Position ({unit})", min_value=0.0, key=f"cutout_x_{i}") * unit_factor
    cy = st.number_input(f"Cutout {i+1} Y Position ({unit})", min_value=0.0, key=f"cutout_y_{i}") * unit_factor
    cw = st.number_input(f"Cutout {i+1} Width ({unit})", min_value=0.0, key=f"cutout_w_{i}") * unit_factor
    ch = st.number_input(f"Cutout {i+1} Height ({unit})", min_value=0.0, key=f"cutout_h_{i}") * unit_factor
    cutouts.append((cx, cy, cw, ch))

# --- Plotting ---
fig_width = max(6, wall_width / 30)
fig_height = max(6, wall_height / 30)
fig, ax = plt.subplots(figsize=(fig_width, fig_height))
ax.set_xlim(0, wall_width)
ax.set_ylim(0, wall_height)
ax.set_aspect('equal')
ax.set_xticks(range(0, int(wall_width) + 1, int(unit_factor * 10)))
ax.set_yticks(range(0, int(wall_height) + 1, int(unit_factor * 10)))
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

        draw_width = min(tile_width, wall_width - tile_x)
        draw_height = min(tile_height, wall_height - tile_y)

        # Check all cutouts
        overlap_area = 0
        for cutout_x, cutout_y, cutout_w, cutout_h in cutouts:
            overlap_x = max(0, min(tile_x + draw_width, cutout_x + cutout_w) - max(tile_x, cutout_x))
            overlap_y = max(0, min(tile_y + draw_height, cutout_y + cutout_h) - max(tile_y, cutout_y))
            overlap_area += overlap_x * overlap_y

        tile_area = tile_width * tile_height
        usable_ratio = 1 - (overlap_area / tile_area)

        if usable_ratio <= 0.05:
            continue

        is_cut = usable_ratio < 1
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

# Draw cutouts
for cutout_x, cutout_y, cutout_w, cutout_h in cutouts:
    if cutout_w > 0 and cutout_h > 0:
        ax.add_patch(patches.Rectangle((cutout_x, cutout_y), cutout_w, cutout_h, fill=True, color='white', edgecolor='black'))
        if show_measurements:
            ax.text(cutout_x + cutout_w / 2, cutout_y - 5, f"{round(cutout_w / unit_factor)}{unit[0]}", ha='center', color='blue')
            ax.text(cutout_x - 3, cutout_y + cutout_h / 2, f"{round(cutout_h / unit_factor)}{unit[0]}", va='center', rotation=90, color='blue')

if show_measurements:
    ax.text(wall_width / 2, wall_height + 2, f"{round(wall_width / unit_factor)}{unit[0]}", ha='center', color='blue')
    ax.text(-3, wall_height / 2, f"{round(wall_height / unit_factor)}{unit[0]}", va='center', rotation=90, color='blue')

ax.invert_yaxis()
st.pyplot(fig)

# --- Tile Count Summary ---
st.subheader("Tile Count Summary")
st.write(f"**Full Tiles:** {full_tiles}")
st.write(f"**Cut Tiles:** {cut_tiles}")
st.write(f"**Total Tiles Required:** {full_tiles + cut_tiles}")
