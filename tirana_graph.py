# =========================================================
# TIRANA FLY — GRAPH I RRUGËVE TË DRONIT
# =========================================================
# Instalimi:
# pip install networkx matplotlib
#
# Ky kod:
# - Krijon graph-in e zonave të Tiranës
# - Vendos 3 magazina:
#       • Magazina Perëndim
#       • Magazina Qendër
#       • Magazina Lindje
# - Lidh secilën magazinë me zonat përkatëse
# - Vizaton graph-in
# =========================================================

import networkx as nx
import matplotlib.pyplot as plt

# =========================================================
# 1. KRIJIMI I GRAPH-IT
# =========================================================

G = nx.Graph()

# =========================================================
# 2. ZONAT E TIRANËS
# =========================================================

zones = {
    "1. Veri": {
        "population": "17.2%",
        "areas": "Bërxullë, Kashar",
        "pos": (0, 8),
    },

    "2. Lindje": {
        "population": "16.8%",
        "areas": "Dajt, Shën Koll",
        "pos": (6, 8),
    },

    "3. Lindje Jug": {
        "population": "14.3%",
        "areas": "Selitë, Kombinat",
        "pos": (7, 3),
    },

    "4. Qendër": {
        "population": "15.5%",
        "areas": "Blloku, Pazari",
        "pos": (3, 6),
    },

    "5. Perëndim": {
        "population": "13.1%",
        "areas": "Kashar, Mezez",
        "pos": (-3, 3),
    },

    "6. Jug Perëndim": {
        "population": "11.8%",
        "areas": "Laprakë, Ali Demi",
        "pos": (-1, 0),
    },

    "7. Jug": {
        "population": "10.6%",
        "areas": "Kom. Parisit",
        "pos": (2, 0),
    },

    "8. Jug Lindje": {
        "population": "10.7%",
        "areas": "Farkë, Petrelë",
        "pos": (6, 0),
    },
}

# =========================================================
# 3. MAGAZINAT (PIKAT E NISJES)
# =========================================================

warehouses = {
    "Magazina Perëndim": {
        "pos": (-3, 5)
    },

    "Magazina Qendër": {
        "pos": (3, 5)
    },

    "Magazina Lindje": {
        "pos": (7, 5)
    },
}

# =========================================================
# 4. SHTIMI I NODE-VE NË GRAPH
# =========================================================

# Zonat
for zone, data in zones.items():

    label = (
        f"{zone}\n"
        f"{data['population']} • {data['areas']}"
    )

    G.add_node(
        zone,
        label=label,
        pos=data["pos"],
        type="zone"
    )

# Magazinat
for warehouse, data in warehouses.items():

    G.add_node(
        warehouse,
        label=warehouse,
        pos=data["pos"],
        type="warehouse"
    )

# =========================================================
# 5. LIDHJET E DRONËVE
# =========================================================

# Magazina Perëndim
G.add_edge("Magazina Perëndim", "1. Veri")
G.add_edge("Magazina Perëndim", "5. Perëndim")
G.add_edge("Magazina Perëndim", "6. Jug Perëndim")

# Magazina Qendër
G.add_edge("Magazina Qendër", "4. Qendër")
G.add_edge("Magazina Qendër", "7. Jug")
G.add_edge("Magazina Qendër", "8. Jug Lindje")

# Magazina Lindje
G.add_edge("Magazina Lindje", "2. Lindje")
G.add_edge("Magazina Lindje", "3. Lindje Jug")

# =========================================================
# 6. POZICIONET
# =========================================================

pos = nx.get_node_attributes(G, "pos")

# =========================================================
# 7. NDARJA E NODE-VE
# =========================================================

zone_nodes = [
    n for n, attr in G.nodes(data=True)
    if attr["type"] == "zone"
]

warehouse_nodes = [
    n for n, attr in G.nodes(data=True)
    if attr["type"] == "warehouse"
]

# =========================================================
# 8. VIZATIMI I GRAPH-IT
# =========================================================

plt.figure(figsize=(14, 9))
plt.style.use("dark_background")

# ---------------------------------------------------------
# Zonat
# ---------------------------------------------------------

nx.draw_networkx_nodes(
    G,
    pos,
    nodelist=zone_nodes,
    node_size=7000,
    node_color="#F3F4F6",
    edgecolors="#D1D5DB",
    linewidths=2,
)

# ---------------------------------------------------------
# Magazinat
# ---------------------------------------------------------

nx.draw_networkx_nodes(
    G,
    pos,
    nodelist=warehouse_nodes,
    node_size=2600,
    node_color="#E76F51",
    edgecolors="#111111",
    linewidths=2,
)

# ---------------------------------------------------------
# Lidhjet
# ---------------------------------------------------------

nx.draw_networkx_edges(
    G,
    pos,
    width=2,
    edge_color="#6EE7B7",
    style="dashed",
)

# =========================================================
# 9. LABELS
# =========================================================

labels = nx.get_node_attributes(G, "label")

nx.draw_networkx_labels(
    G,
    pos,
    labels=labels,
    font_size=11,
    font_weight="bold",
)

# =========================================================
# 10. TITULLI
# =========================================================

plt.title(
    "TIRANA FLY — GRAPH I RRUGËVE TË DRONËVE",
    fontsize=20,
    fontweight="bold",
    pad=20,
)

plt.axis("off")
plt.tight_layout()

# =========================================================
# 11. SHFAQJA
# =========================================================

plt.show()