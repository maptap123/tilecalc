import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math
import re

st.set_page_config(layout="wide")
st.title("🧱 Smart Shower Tile Layout Visualizer with Grout, Stagger, and Scrap Reuse")

st.markdown("Visualize your shower tiling layout with accurate grout spacing, staggered rows, and intelligent scrap reuse to minimize waste.")

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
    stagger = st.checkbox("Stagger Rows (Brick Pattern)", value=True)
    reuse_scraps = st.checkbox("Reuse Scrap Pieces Where Possible", value=True)
    debug_mode = st.checkbox("Show Debug Info", value=False)
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
scrap_pool = []
scraps_reused = 0
TOLERANCE = 0.1

# Draw tiles
for j in range(tiles_up):
    row_y = j * tile_full_height
    is_staggered = stagger and (j % 2 == 1)
    offset_x = (tile_full_width / 2) if is_staggered else 0

    # Reuse half-tile if available at row start
    if is_staggered and reuse_scraps:
        if "half-tile" in scrap_pool:
            rect = patches.Rectangle((0, row_y), tile_width / 2, tile_height, linewidth=1.5, edgecolor='blue', facecolor='lightgray')
            ax.add_patch(rect)
            scrap_pool.remove("half-tile")
            cut_tiles += 1
            scraps_reused += 1

    for i in range(tiles_across + 1):
        tile_x = i * tile_full_width + offset_x
        tile_y = row_y

        if tile_y >= wall_height:
            continue

        # NEW: Pre-check if the remaining space is half a tile
        if not is_staggered and abs((wall_width - tile_x) - tile_width / 2) < TOLERANCE:
            scrap_pool.append("half-tile")

        draw_width = tile_width
        draw_height = tile_height

        if wall_width - tile_x < tile_width - TOLERANCE:
            draw_width = wall_width - tile_x
        if wall_height - tile_y < tile_height - TOLERANCE:
            draw_height = wall_height - tile_y

        if draw_width <= 0 or draw_height <= 0:
            continue

        is_cut = False
        edgecolor = 'gray'

        # Scrap reuse matching
        if reuse_scraps and draw_width < tile_width - TOLERANCE:
            match_label = None
            if abs(draw_width - tile_width / 2) < TOLERANCE and "half-tile" in scrap_pool:
                match_label = "half-tile"
            elif str(round(draw_width, 1)) in scrap_pool:
                match_label = str(round(draw_width, 1))

            if match_label:
                scrap_pool.remove(match_label)
                edgecolor = 'blue'
                is_cut = True
                scraps_reused += 1
            else:
                if abs(draw_width - tile_width / 2) < TOLERANCE:
                    scrap_pool.append("half-tile")
                else:
                    scrap_pool.append(str(round(tile_width - draw_width, 1)))
                edgecolor = 'red'
                is_cut = True

        elif draw_width < tile_width - TOLERANCE:
            if abs(draw_width - tile_width / 2) < TOLERANCE:
                scrap_pool.append("half-tile")
            else:
                scrap_pool.append(str(round(tile_width - draw_width, 1)))
            edgecolor = 'red'
            is_cut = True

        # Cutout collision
        overlap_area = 0
        for cutout_x, cutout_y, cutout_w, cutout_h in cutouts:
            overlap_x = max(0, min(tile_x + draw_width, cutout_x + cutout_w) - max(tile_x, cutout_x))
            overlap_y = max(0, min(tile_y + draw_height, cutout_y + cutout_h) - max(tile_y, cutout_y))
            overlap_area += overlap_x * overlap_y

        tile_area = tile_width * tile_height
        usable_ratio = 1 - (overlap_area / tile_area)
        if usable_ratio <= 0.05:
            continue
        elif usable_ratio < 1:
            is_cut = True
            edgecolor = 'red'

        rect = patches.Rectangle((tile_x, tile_y), draw_width, draw_height,
                                 linewidth=1.5 if edgecolor == 'blue' else 1, edgecolor=edgecolor, facecolor='lightgray')
        ax.add_patch(rect)

        if is_cut:
            cut_tiles += 1
        else:
            full_tiles += 1

# Wall outline
ax.add_patch(patches.Rectangle((0, 0), wall_width, wall_height, fill=False, edgecolor='black', linewidth=2))

# Cutouts
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
st.write(f"**Scraps Reused:** {scraps_reused}")
if debug_mode:
    st.write("Scrap Pool:", scrap_pool)
