import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math
import re

st.set_page_config(layout="wide")
st.title("🧱 Custom Shower Tile Layout Visualizer with Cutouts, Grout, and Stagger")

st.markdown("Enter wall and tile dimensions to visualize your tiling layout, including cut tiles, grout spacing, and staggering.")

# --- Parse input like 5'11" or 2'0.5"
def parse_feet_inches(value):
    try:
        match = re.match(r"(?:(\d+)'\s*)?(\d+(?:\.\d*)?)?\"?", value.strip())
        if match:
            feet = float(match.group(1) or 0)
            inches = float(match.group(2) or 0)
            return feet * 12 + inches
    except:
        pass
    return 0.0

# --- Unit input with feet/inches parser ---
def dimension_input(label, default_str, key):
    text_val = st.text_input(label, value=default_str, key=key)
    return parse_feet_inches(text_val)

# --- Wall and Tile Inputs ---
col1, col2 = st.columns(2)
with col1:
    wall_width = dimension_input("Wall Width (e.g., 5'11\")", "5'0\"", "wall_width")
    wall_height = dimension_input("Wall Height", "7'6\"", "wall_height")
with col2:
    tile_width = dimension_input("Tile Width", "1'0\"", "tile_width")
    tile_height = dimension_input("Tile Height", "1'0\"", "tile_height")
    grout_w = st.number_input("Grout Spacing Horizontal (in)", min_value=0.0, value=0.25)
    grout_h = st.number_input("Grout Spacing Vertical (in)", min_value=0.0, value=0.25)
    stagger = st.checkbox("Stagger Rows (Brick Pattern)", value=False)
    show_grid = st.checkbox("Show Grid", value=True)
    show_measurements = st.checkbox("Show Measurements", value=True)

# --- Multiple Cutouts ---
st.subheader("Cutouts")
num_cutouts = st.number_input("Number of Cutouts", min_value=0, max_value=5, value=1)
cutouts = []
for i in range(int(num_cutouts)):
    st.markdown(f"**Cutout {i+1}**")
    cx = dimension_input(f"Cutout {i+1} X Position", "3'0\"", f"cutout_x_{i}")
    cy = dimension_input(f"Cutout {i+1} Y Position", "0'0\"", f"cutout_y_{i}")
    cw = dimension_input(f"Cutout {i+1} Width", "1'0\"", f"cutout_w_{i}")
    ch = dimension_input(f"Cutout {i+1} Height", "1'0\"", f"cutout_h_{i}")
    cutouts.append((cx, cy, cw, ch))

# --- Plotting ---
fig_width = max(6, wall_width / 30)
fig_height = max(6, wall_height / 30)
fig, ax = plt.subplots(figsize=(fig_width, fig_height))
ax.set_xlim(0, wall_width)
ax.set_ylim(0, wall_height)
ax.set_aspect('equal')
ax.set_xticks(range(0, int(wall_width) + 1, 10))
ax.set_yticks(range(0, int(wall_height) + 1, 10))
if show_grid:
    ax.grid(True, which='both', color='lightgrey', linewidth=0.5)

# Tiling calculation
tile_full_width = tile_width + grout_w
tile_full_height = tile_height + grout_h
tiles_across = math.ceil(wall_width / tile_full_width)
tiles_up = math.ceil(wall_height / tile_full_height)

full_tiles = 0
cut_tiles = 0

# Draw tiles
for j in range(tiles_up):
    for i in range(tiles_across):
        offset_x = (tile_full_width / 2) if (stagger and j % 2 == 1) else 0
        tile_x = i * tile_full_width + offset_x
        tile_y = j * tile_full_height

        if tile_x >= wall_width or tile_y >= wall_height:
            continue

        draw_width = min(tile_width, wall_width - tile_x)
        draw_height = min(tile_height, wall_height - tile_y)

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
            ax.text(cutout_x + cutout_w / 2, cutout_y - 5, f"{round(cutout_w)}\"", ha='center', color='blue')
            ax.text(cutout_x - 3, cutout_y + cutout_h / 2, f"{round(cutout_h)}\"", va='center', rotation=90, color='blue')

if show_measurements:
    ax.text(wall_width / 2, wall_height + 2, f"{round(wall_width)}\"", ha='center', color='blue')
    ax.text(-3, wall_height / 2, f"{round(wall_height)}\"", va='center', rotation=90, color='blue')

ax.invert_yaxis()
st.pyplot(fig)

# --- Tile Count Summary ---
st.subheader("Tile Count Summary")
st.write(f"**Full Tiles:** {full_tiles}")
st.write(f"**Cut Tiles:** {cut_tiles}")
st.write(f"**Total Tiles Required:** {full_tiles + cut_tiles}")
