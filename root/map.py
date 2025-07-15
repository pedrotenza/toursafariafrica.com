import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from PIL import Image, ImageFilter, ImageOps
import requests
from io import BytesIO

# --- 1. Set up the map ---
fig = plt.figure(figsize=(12, 10))
ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
ax.set_extent([10, 30, -35, -17])  # Roughly Namibia, Botswana, South Africa

# Add geographic features
ax.add_feature(cfeature.LAND, color='#e6d8ad')  # Parchment-like land
ax.add_feature(cfeature.OCEAN, color='#8b9fa6')  # Aged blue ocean
ax.add_feature(cfeature.BORDERS, linestyle=':', linewidth=1, edgecolor='#5a3921')  # Country borders
ax.add_feature(cfeature.RIVERS, edgecolor='#5a8fad')  # Rivers
ax.add_feature(cfeature.LAKES, edgecolor='#5a8fad', facecolor='#8b9fa6')

# --- 2. Label key locations ---
locations = {
    # Namibia
    "Etosha": {"xy": (16.5, -18.75), "color": "#5a3921", "icon": "🦓"},
    "Sossusvlei": {"xy": (15.8, -24.7), "color": "#a6421a", "icon": "🏜️"},
    # South Africa
    "Kruger": {"xy": (31.5, -24.0), "color": "#5a3921", "icon": "🦁"},
    # Botswana
    "Okavango": {"xy": (22.4, -19.3), "color": "#5a3921", "icon": "🌿"},
    "Chobe": {"xy": (24.7, -18.6), "color": "#5a3921", "icon": "🐘"},
}

for name, props in locations.items():
    ax.annotate(
        props["icon"] + " " + name,
        xy=props["xy"],
        xycoords=ccrs.PlateCarree(),
        color=props["color"],
        fontsize=12,
        fontfamily="serif",
        ha="center",
        bbox=dict(boxstyle="round,pad=0.2", fc="#f0e6cc", ec="none", alpha=0.7),
    )

# --- 3. Add medieval-style decorations ---
ax.annotate(
    "Here be Lions",
    xy=(25, -28),
    xycoords=ccrs.PlateCarree(),
    color="#5a3921",
    fontsize=10,
    fontstyle="italic",
    ha="center",
)

# Compass Rose
ax.annotate(
    "▲\nN",
    xy=(28, -18),
    xycoords=ccrs.PlateCarree(),
    color="#5a3921",
    fontsize=16,
    ha="center",
    va="center",
)

# --- 4. Export and age the map ---
plt.savefig("africa_map.png", dpi=300, bbox_inches="tight", pad_inches=0.2)
plt.close()

# --- 5. Apply parchment texture & aging ---
# Load a parchment texture (or generate one)
texture_url = "https://raw.githubusercontent.com/python-visualization/folium/main/examples/data/parchment_texture.jpg"
texture = Image.open(BytesIO(requests.get(texture_url).content)).resize((1200, 1000))

# Load the map and blend with texture
map_img = Image.open("africa_map.png").convert("RGBA")
texture = texture.convert("RGBA")
final_map = Image.blend(map_img, texture, alpha=0.4)

# Add burn marks (optional)
final_map.filter(ImageFilter.GaussianBlur(0.5))  # Soften edges
final_map = ImageOps.autocontrast(final_map, cutoff=2)

# Save final map
final_map.save("medieval_africa_map.png")
print("Map generated: medieval_africa_map.png")