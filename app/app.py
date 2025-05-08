import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math
import re

st.set_page_config(layout="wide")
st.title("🧱 Smart Shower Tile Layout Visualizer with Grout, Stagger, and Cuttable Scrap Reuse")

st.markdown("Visualize your shower tiling layout with accurate grout spacing, staggered rows, cutouts, and smart scrap reuse — even cut-to-fit!")

# Parse 5'11" input
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

def dimension_input(label, default_str, key):
    text_val = st.text_input(label, value=default_str, key=key)
    return parse_feet_inches(text_val)

# Inputs
col1, col2 = st.columns(2)
with col1:
    wall_width = dimension_input("Wall Width", "5'0\"", "wall_width")
    wall_height = dimension_input("Wall Height", "7'6\"", "wall_height")
with col2:
    tile_width = dimension_input("Tile Width", "1'0\"", "tile_width")
    tile_height = dimension_input("Tile Height", "1'0\"", "tile_height")
    grout_w = st.number_input("Grout Spacing Horizontal (in)", min_value=0.0, value=0.25)
    grout_h = st.number_input("Grout Spacing Vertical (in)", min_value=0.0, value=0.25)
    stagger = st.checkbox("Stagger Rows", True)
    reuse_scraps = st.checkbox("Reuse and Cut Scraps", True)
    debug_mode = st.checkbox("Show Debug Info", False)

# Cutout input
st.subheader("Cutouts")
num_cutouts = st.number_input("Number of Cutouts", min_value=0, max_value=5, value=0)
cutouts = []
for i in range(int(num_cutouts)):
    st.markdown(f"**Cutout {i+1}**")
    cx = dimension_input(f"Cutout {i+1} X Position", "3'0\"", f"cutout_x_{i}")
    cy = dimension_input(f"Cutout {i+1} Y Position", "0'0\"", f"cutout_y_{i}")
    cw = dimension_input(f"Cutout {i+1} Width", "1'0\"", f"cutout_w_{i}")
    ch = dimension_input(f"Cutout {i+1} Height", "1'0\"", f"cutout_h_{i}")
    cutouts.append((cx, cy, cw, ch))

# Constants
TOLERANCE = 0.1
full_tiles = 0
cut_tiles = 0
scraps_reused = 0
scrap_pool = []

# Setup
tile_full_width = tile_width + grout_w
tile_full_height = tile_height + grout_h
tiles_across = math.ceil(wall_width / tile_full_width)
tiles_up = math.ceil(wall_height / tile_full_height)

fig, ax = plt.subplots(figsize=(wall_width / 10, wall_height / 10))
ax.set_xlim(0, wall_width)
ax.set_ylim(0, wall_height)
ax.set_aspect('equal')

# Draw tiles
for j in range(tiles_up):
    row_y = j * tile_full_height
    is_staggered = stagger and (j % 2 == 1)
    offset_x = tile_full_width / 2 if is_staggered else 0

    # Reuse OR cut a new tile for staggered left-start
    if is_staggered:
        needed = tile_width / 2
        matched = None
        for s in sorted(scrap_pool):
            if s >= needed - TOLERANCE:
                matched = s
                break
        if matched:
            scrap_pool.remove(matched)
            remaining = round(matched - needed, 2)
            if remaining > TOLERANCE:
                scrap_pool.append(remaining)
            edgecolor = 'blue'
            scraps_reused += 1
        else:
            leftover = tile_width - needed
            scrap_pool.append(round(leftover, 2))
            edgecolor = 'red'
        ax.add_patch(patches.Rectangle((0, row_y), needed, tile_height, edgecolor=edgecolor, facecolor='lightgray'))
        cut_tiles += 1

    x = 0
    while x < wall_width:
        tile_x = x + offset_x
        if tile_x >= wall_width:
            break

        remaining_width = wall_width - tile_x
        draw_width = min(tile_width, remaining_width)
        leftover = round(tile_width - draw_width, 2)
        is_cut = draw_width < tile_width - TOLERANCE or draw_width < tile_width

        reused = False
        if draw_width > 0 and reuse_scraps:
            for scrap in sorted(scrap_pool):
                if scrap >= draw_width - TOLERANCE:
                    scrap_pool.remove(scrap)
                    remaining = round(scrap - draw_width, 2)
                    if remaining > TOLERANCE:
                        scrap_pool.append(remaining)
                    edgecolor = 'blue'
                    reused = True
                    scraps_reused += 1
                    break

        if not reused and is_cut:
            scrap_pool.append(leftover)
            edgecolor = 'red'
        elif reused:
            edgecolor = 'blue'
        else:
            edgecolor = 'gray'

        # Cutout collision check
        overlap_area = 0
        for cutout_x, cutout_y, cutout_w, cutout_h in cutouts:
            overlap_x = max(0, min(tile_x + draw_width, cutout_x + cutout_w) - max(tile_x, cutout_x))
            overlap_y = max(0, min(row_y + tile_height, cutout_y + cutout_h) - max(row_y, cutout_y))
            overlap_area += overlap_x * overlap_y

        tile_area = tile_width * tile_height
        usable_ratio = 1 - (overlap_area / tile_area)
        if usable_ratio <= 0.05:
            x += tile_full_width
            continue
        elif usable_ratio < 1:
            is_cut = True
            edgecolor = 'red'

        ax.add_patch(patches.Rectangle((tile_x, row_y), draw_width, tile_height,
                                       edgecolor=edgecolor, facecolor='lightgray', linewidth=1.5 if edgecolor == 'blue' else 1))
        if is_cut or reused:
            cut_tiles += 1
        else:
            full_tiles += 1

        x += tile_full_width

# Draw wall and cutouts
ax.add_patch(patches.Rectangle((0, 0), wall_width, wall_height, fill=False, edgecolor='black', linewidth=2))
for cutout_x, cutout_y, cutout_w, cutout_h in cutouts:
    ax.add_patch(patches.Rectangle((cutout_x, cutout_y), cutout_w, cutout_h, fill=True, color='white', edgecolor='black'))

ax.invert_yaxis()
st.pyplot(fig)

# Output
st.subheader("Tile Count Summary")
st.write(f"Full Tiles: {full_tiles}")
st.write(f"Cut Tiles: {cut_tiles}")
st.write(f"Total Tiles: {full_tiles + cut_tiles}")
st.write(f"Scraps Reused: {scraps_reused}")
if debug_mode:
    st.write("Scrap Pool (inches):", scrap_pool)
