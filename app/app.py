import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math
import re

st.set_page_config(page_title="Tile Layout Visualizer", layout="wide")

st.markdown("""
    <style>
        body {
            background-color: #f7f1e1;
        }
        .block-container {
            background-color: #fff8e7;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        }
        input, select, textarea {
            background-color: #fdf6e3 !important;
            border-radius: 5px;
        }
        .stSlider > div[data-baseweb="slider"] > div {
            background-color: #c3b091;
        }
    </style>
""", unsafe_allow_html=True)
st.markdown("""
    <h1 style='text-align: center; color: #3E4E88;'>🧱 Tile Layout Visualizer</h1>
    <p style='text-align: center; font-size: 18px;'>Plan smarter. Cut cleaner. Save tiles.</p>
""", unsafe_allow_html=True)

st.markdown("""
    <div style='background-color: #f0f2f6; padding: 10px; border-left: 5px solid #3E4E88;'>
    💡 This tool helps visualize tile layouts with cutout areas, staggered patterns, and real-time scrap tracking.
    </div>
""", unsafe_allow_html=True)

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
    layout_style = st.selectbox("Tile Pattern", [
        "Straight",
        "Staggered (½ Offset)",
        "One-third Offset"
    ])
    reuse_scraps = st.checkbox("Reuse and Cut Scraps", True)
    debug_mode = st.checkbox("Show Debug Info", False)

# Cutouts
st.subheader("Cutouts")
num_cutouts = st.number_input("Number of Cutouts", min_value=0, max_value=5, value=0)
cutouts = []
for i in range(int(num_cutouts)):
    st.markdown(f"**Cutout {i+1}**")
    name = st.text_input(f"Cutout {i+1} Name", f"Cutout {i+1}", key=f"cutout_name_{i}")
    cx = dimension_input(f"Cutout {i+1} X Position", "3'0\"", f"cutout_x_{i}")
    cy = dimension_input(f"Cutout {i+1} Y Position", "0'0\"", f"cutout_y_{i}")
    cw = dimension_input(f"Cutout {i+1} Width", "1'0\"", f"cutout_w_{i}")
    ch = dimension_input(f"Cutout {i+1} Height", "1'0\"", f"cutout_h_{i}")
    cutouts.append((name, cx, cy, cw, ch))

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

scale = min(1, 10 / max(wall_width, wall_height))
zoom = st.slider("Zoom", 0.5, 2.0, 1.0, 0.1)
fig_width = wall_width * scale * zoom
fig_height = wall_height * scale * zoom
fig, ax = plt.subplots(figsize=(fig_width, fig_height))
ax.set_xlim(0, wall_width)
ax.set_ylim(0, wall_height)
ax.set_aspect('equal')

# Tiling logic
for j in range(tiles_up):
    row_y = j * tile_full_height
    if layout_style == "Staggered (½ Offset)":
        offset_x = (j % 2) * (tile_width / 2 + grout_w / 2)
    elif layout_style == "One-third Offset":
        offset_x = (j % 3) * (tile_width / 3 + grout_w / 3)
    else:
        offset_x = 0

    if offset_x > 0:
        needed = offset_x
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
            if leftover > TOLERANCE:
                scrap_pool.append(round(leftover, 2))
            edgecolor = 'red'
        ax.add_patch(patches.Rectangle((0, row_y), needed, tile_height, edgecolor=edgecolor, facecolor='#d9cbb3'))
        cut_tiles += 1

    for i in range(tiles_across + 1):
        tile_x = i * tile_full_width + offset_x
        if tile_x >= wall_width:
            break

        draw_width = min(tile_width, wall_width - tile_x)
        draw_height = tile_height
        leftover = round(tile_width - draw_width, 2)
        is_cut = draw_width < tile_width - TOLERANCE

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

        overlap_area = 0
        for _, cutout_x, cutout_y, cutout_w, cutout_h in cutouts:
            overlap_x = max(0, min(tile_x + draw_width, cutout_x + cutout_w) - max(tile_x, cutout_x))
            overlap_y = max(0, min(row_y + tile_height, cutout_y + cutout_h) - max(row_y, cutout_y))
            overlap_area += overlap_x * overlap_y

        tile_area = tile_width * tile_height
        usable_ratio = 1 - (overlap_area / tile_area)
        if usable_ratio <= 0.05:
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

# Draw wall + cutouts
ax.add_patch(patches.Rectangle((0, 0), wall_width, wall_height, fill=False, edgecolor='black', linewidth=2))
for name, cutout_x, cutout_y, cutout_w, cutout_h in cutouts:
    ax.add_patch(patches.Rectangle((cutout_x, cutout_y), cutout_w, cutout_h, fill=True, color='white', edgecolor='black'))
    ax.text(cutout_x + cutout_w / 2, cutout_y + cutout_h / 2, name, ha='center', va='center', fontsize=8, color='black')

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
