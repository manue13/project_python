# =========================================================
# TIRANA FLY — DATA
# Zones, Warehouses, Client Generation
# =========================================================

import random
import math

random.seed(42)

# =========================================================
# ZONES
# Each zone has:
#   - display name
#   - sub-areas label
#   - population share
#   - graph position (x, y) — for layout
#   - bounding box (x_min, x_max, y_min, y_max) — for client scatter
#   - supplying warehouse
# =========================================================

ZONES = {
    "1. Veri": {
        "label":     "1. VERI\nBërxullë · Kashar · Yzberisht",
        "pct":       "17.2%",
        "pos":       (1,  9),
        "bbox":      (0,  2,  8, 10),
        "warehouse": "Magazina Perëndim",
        "color":     "#5B9BD5",
    },
    "2. Lindje": {
        "label":     "2. LINDJE\nDajt · Paskuqan · Shën Koll",
        "pct":       "16.8%",
        "pos":       (8,  9),
        "bbox":      (7, 10,  8, 10),
        "warehouse": "Magazina Lindje",
        "color":     "#70B244",
    },
    "3. Lindje Jug": {
        "label":     "3. LINDJE JUG\nLiqeni Art. · Selitë · Kombinat",
        "pct":       "14.3%",
        "pos":       (9,  5),
        "bbox":      (8, 11,  4,  8),
        "warehouse": "Magazina Lindje",
        "color":     "#F4C144",
    },
    "4. Qendër": {
        "label":     "4. QENDËR\nSkënderbej · Blloku · Pazari i Ri",
        "pct":       "15.5%",
        "pos":       (5,  6),
        "bbox":      (4,  7,  5,  8),
        "warehouse": "Magazina Qendër",
        "color":     "#E05A4E",
    },
    "5. Perëndim": {
        "label":     "5. PERËNDIM\nKashar · Vaqarr · Mezez",
        "pct":       "13.1%",
        "pos":       (1,  6),
        "bbox":      (0,  3,  5,  8),
        "warehouse": "Magazina Perëndim",
        "color":     "#F0872D",
    },
    "6. Jug Perëndim": {
        "label":     "6. JUG PERËNDIM\nLaprakë · Don Bosko · Ali Demi",
        "pct":       "11.8%",
        "pos":       (2,  2),
        "bbox":      (0,  4,  1,  4),
        "warehouse": "Magazina Perëndim",
        "color":     "#3BAAA0",
    },
    "7. Jug": {
        "label":     "7. JUG\nKomuna e Parisit · Myslym Shyri",
        "pct":       "10.6%",
        "pos":       (5,  2),
        "bbox":      (4,  7,  1,  4),
        "warehouse": "Magazina Qendër",
        "color":     "#7B62B5",
    },
    "8. Jug Lindje": {
        "label":     "8. JUG LINDJE\nFarkë · Qesarak · Petrelë",
        "pct":       "10.7%",
        "pos":       (8,  2),
        "bbox":      (7, 11,  1,  4),
        "warehouse": "Magazina Lindje",
        "color":     "#E884A8",
    },
}

# =========================================================
# WAREHOUSES
# Each warehouse supplies specific zones (see above).
# Positions are fixed in graph space.
# =========================================================

WAREHOUSES = {
    "Magazina Perëndim": {
        "pos":    (0,  6),
        "color":  "#FF6B6B",
        "zones":  ["1. Veri", "5. Perëndim", "6. Jug Perëndim"],
    },
    "Magazina Qendër": {
        "pos":    (5,  5),
        "color":  "#FFD93D",
        "zones":  ["4. Qendër", "7. Jug"],
    },
    "Magazina Lindje": {
        "pos":    (9,  6),
        "color":  "#6BCB77",
        "zones":  ["2. Lindje", "3. Lindje Jug", "8. Jug Lindje"],
    },
}

# =========================================================
# CLIENT GENERATION
# Each zone gets at least 16 clients scattered inside its
# bounding box.  Clients are numbered zone-locally.
# =========================================================

CLIENTS_PER_ZONE = 16   # minimum

def _scatter_clients(zone_name: str, bbox: tuple, n: int) -> list[dict]:
    """Return n client dicts placed randomly inside bbox."""
    x_min, x_max, y_min, y_max = bbox
    clients = []
    for i in range(n):
        x = round(random.uniform(x_min, x_max), 3)
        y = round(random.uniform(y_min, y_max), 3)
        clients.append({
            "id":   f"{zone_name}_K{i+1:02d}",
            "zone": zone_name,
            "pos":  (x, y),
        })
    return clients


def generate_all_clients(n: int = CLIENTS_PER_ZONE) -> dict[str, list[dict]]:
    """Return {zone_name: [client, ...]} for all zones."""
    return {
        zone: _scatter_clients(zone, data["bbox"], n)
        for zone, data in ZONES.items()
    }

# =========================================================
# DISTANCE UTILITY
# =========================================================

def euclidean(p1: tuple, p2: tuple) -> float:
    return round(math.sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2), 3)
