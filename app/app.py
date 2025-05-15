import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math
import re
import io
from matplotlib.backends.backend_pdf import PdfPages
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

st.set_page_config(page_title="Tile Layout Visualizer", layout="wide")
st.title("🧱 Smart Shower Tile Layout Visualizer with Advanced Patterns and Scrap Reuse")
st.markdown("Visualize tile layouts across multiple walls with cutouts, staggered patterns, and real-time scrap tracking.")

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

# Tile settings
st.sidebar.header("🧱 Tile Settings")
tile_width = dimension_input("Tile Width", "1'0\"", "tile_width")
tile_height = dimension_input("Tile Height", "1'0\"", "tile_height")
grout_w = st.number_input("Grout Spacing Horizontal (in)", min_value=0.0, value=0.25)
grout_h = st.number_input("Grout Spacing Vertical (in)", min_value=0.0, value=0.25)
layout_style = st.selectbox("Tile Pattern", ["Straight", "Staggered (½ Offset)", "One-third Offset"])
reuse_scraps = st.checkbox("Reuse and Cut Scraps", True)
debug_mode = st.checkbox("Show Debug Info", False)
show_3d = st.checkbox("🔍 View 3D Layout (3 Walls Only)")

# Wall setup
st.subheader("Wall Setup")
num_walls = st.number_input("Number of Walls", min_value=1, max_value=5, value=3)
walls = []
for i in range(int(num_walls)):
    st.markdown(f"### Wall {chr(65+i)}")
    width = dimension_input(f"Wall {chr(65+i)} Width", "5'0\"", f"wall_width_{i}")
    height = dimension_input(f"Wall {chr(65+i)} Height", "7'6\"", f"wall_height_{i}")
    walls.append({"label": f"Wall {chr(65+i)}", "width": width, "height": height})

# Cutouts
st.subheader("Cutouts")
num_cutouts = st.number_input("Number of Cutouts", min_value=0, max_value=10, value=0)
cutouts = []
wall_labels = [w["label"] for w in walls]

for i in range(int(num_cutouts)):
    st.markdown(f"**Cutout {i+1}**")
    name = st.text_input(f"Cutout {i+1} Name", f"Cutout {i+1}", key=f"cutout_name_{i}")
    assigned_wall = st.selectbox(f"Cutout {i+1} Wall", wall_labels, key=f"cutout_wall_{i}")
    cx = dimension_input(f"Cutout {i+1} X Position (relative to wall)", "3'0\"", f"cutout_x_{i}")
    cy = dimension_input(f"Cutout {i+1} Y Position", "0'0\"", f"cutout_y_{i}")
    cw = dimension_input(f"Cutout {i+1} Width", "1'0\"", f"cutout_w_{i}")
    ch = dimension_input(f"Cutout {i+1} Height", "1'0\"", f"cutout_h_{i}")
    cutouts.append((name, assigned_wall, cx, cy, cw, ch))

# If 3D mode is on, show basic 3D preview
if show_3d and len(walls) == 3:
    fig = plt.figure(figsize=(10, 6))
    ax = fig.add_subplot(111, projection='3d')

    wall_A = walls[0]  # Left
    wall_B = walls[1]  # Center
    wall_C = walls[2]  # Right

    def draw_wall(ax, start_x, start_y, start_z, dir_x, dir_z, wall, label):
        tile_full_width = tile_width + grout_w
        tile_full_height = tile_height + grout_h
        tiles_across = int(wall["width"] // tile_full_width)
        tiles_up = int(wall["height"] // tile_full_height)

        for i in range(tiles_across):
            for j in range(tiles_up):
                x = start_x + i * tile_full_width * dir_x
                y = start_y + j * tile_full_height
                z = start_z + i * tile_full_width * dir_z
                dx = tile_width * dir_x
                dz = tile_width * dir_z
                ax.bar3d(x, y, z, dx, tile_height, dz, color='lightgray', edgecolor='black', alpha=0.8)

        ax.text(start_x + dir_x * wall["width"] / 2,
                start_y + wall["height"] + 2,
                start_z + dir_z * wall["width"] / 2,
                label, color='black', ha='center', fontsize=10)

    draw_wall(ax, 0, 0, 0, 0, 1, wall_A, wall_A["label"])
    draw_wall(ax, 0, 0, wall_A["width"], 1, 0, wall_B, wall_B["label"])
    draw_wall(ax, wall_B["width"], 0, wall_A["width"], 0, -1, wall_C, wall_C["label"])

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.set_xlim(0, wall_B["width"] + wall_C["width"])
    ax.set_ylim(0, max(w["height"] for w in walls))
    ax.set_zlim(0, wall_A["width"] + wall_C["width"])
    st.pyplot(fig)
else:
    st.warning("3D view is only available when 3 walls are configured.")
