import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from PIL import Image, ImageFilter, ImageOps

# --- 1. CONFIGURACIÓN DEL MAPA ---
fig = plt.figure(figsize=(14, 12))
ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
ax.set_extent([12, 34, -35, -17])  # Más amplio para incluir toda Sudáfrica

# --- 2. UBICACIONES PRECISAS (VERIFICADAS) ---
locations = {
    "Etosha": {"xy": (16.5, -18.75), "color": "#2d1a0f"},
    "Sossusvlei": {"xy": (15.8, -24.76), "color": "#8c4c2b"},
    "Okavango": {"xy": (22.45, -19.25), "color": "#1f3d2a"},
    "Chobe": {"xy": (25.2, -17.8), "color": "#3b5a3c"},
    "Kruger": {"xy": (31.5, -24.0), "color": "#2d1a0f"},
}

# --- 3. ELEMENTOS GEOGRÁFICOS ---
ax.add_feature(cfeature.LAND, color='#f5e8c9')  
ax.add_feature(cfeature.OCEAN, color='#a8c4bb')  
ax.add_feature(cfeature.BORDERS, linestyle='--', linewidth=1.2, edgecolor='#5a3921')
ax.add_feature(cfeature.RIVERS, edgecolor='#5a8fad', linewidth=1.5)
ax.add_feature(cfeature.LAKES, edgecolor='#5a8fad', facecolor='#a8c4bb')

# --- 4. AÑADIR MARCADORES ---
for name, props in locations.items():
    ax.annotate(
        name,
        xy=props["xy"],
        xycoords=ccrs.PlateCarree(),
        color=props["color"],
        fontsize=14,
        fontfamily="DejaVu Serif",
        ha="center",
        va="center"
    )

# --- 5. ETIQUETAS DE PAÍSES ---
country_labels = {
    "NAMIBIA": {"xy": (17.5, -21.5), "fontsize": 18, "color": "#2d1a0f"},
    "BOTSWANA": {"xy": (24.0, -21.0), "fontsize": 18, "color": "#2d1a0f"},
    "SOUTH AFRICA": {"xy": (24.5, -30.0), "fontsize": 18, "color": "#2d1a0f"}
}

for country, props in country_labels.items():
    ax.annotate(
        country,
        xy=props["xy"],
        xycoords=ccrs.PlateCarree(),
        color=props["color"],
        fontsize=props["fontsize"],
        fontfamily="DejaVu Serif",
        fontweight="bold",
        ha="center",
        va="center"
    )

# --- 6. ELEMENTOS DECORATIVOS ---
ax.annotate("▲ NORTE", xy=(30.5, -18.5), color="#2d1a0f", fontsize=12, ha="center")
ax.annotate("Here be Lions", xy=(25.5, -25.8), color="#5a3921", fontstyle="italic", ha="center")

# --- 7. EXPORTAR MAPA BASE ---
plt.savefig("africa_map.png", dpi=300, bbox_inches="tight", pad_inches=0.3, facecolor='#f5e8c9')

# No plt.close() ni plt.show() aquí — dejamos que el archivo quede guardado.

# --- 8. PROCESAMIENTO DE IMAGEN ---
def apply_parchment_effect(input_path, output_path):
    map_img = Image.open(input_path).convert('RGB')
    w, h = map_img.size

    texture = Image.new('RGB', (w, h), '#f5e8c9')
    pixels = texture.load()
    for i in range(w):
        for j in range(h):
            if (i + j) % 20 < 10:
                pixels[i,j] = (210, 190, 160)

    final = Image.blend(map_img, texture, alpha=0.25)
    final = final.filter(ImageFilter.GaussianBlur(radius=0.8))
    final = ImageOps.autocontrast(final, cutoff=2)
    final.save(output_path)

apply_parchment_effect("africa_map.png", "medieval_africa_final.png")
print("✅ Mapa generado: 'medieval_africa_final.png'")
