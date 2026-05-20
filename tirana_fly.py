# =========================================================
# TIRANA FLY — ONE FILE, RUN AND SEE IT
# pip install networkx matplotlib
# python3 tirana_fly.py
# =========================================================

import math, random
import matplotlib
matplotlib.use("TkAgg")  # shows a window
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
from matplotlib.patches import Polygon as MplPolygon
from matplotlib.lines import Line2D
import networkx as nx

random.seed(42)

# =========================================================
# DATA
# =========================================================

BG = "#0D1117"

ZONES = {
    "1.Veri":        {"color":"#5B9BD5","pos":(1,9),"pct":"17.2%","wh":"Perëndim"},
    "2.Lindje":      {"color":"#70B244","pos":(8,9),"pct":"16.8%","wh":"Lindje"},
    "3.LindjeJug":   {"color":"#F4C144","pos":(9,5),"pct":"14.3%","wh":"Lindje"},
    "4.Qendër":      {"color":"#E05A4E","pos":(5,6),"pct":"15.5%","wh":"Qendër"},
    "5.Perëndim":    {"color":"#F0872D","pos":(1,6),"pct":"13.1%","wh":"Perëndim"},
    "6.JugPerëndim": {"color":"#3BAAA0","pos":(2,2),"pct":"11.8%","wh":"Perëndim"},
    "7.Jug":         {"color":"#7B62B5","pos":(5,2),"pct":"10.6%","wh":"Qendër"},
    "8.JugLindje":   {"color":"#E884A8","pos":(8,2),"pct":"10.7%","wh":"Lindje"},
}

WAREHOUSES = {
    "Perëndim": {"pos":(0,5.5), "color":"#FF6B6B", "zones":["1.Veri","5.Perëndim","6.JugPerëndim"]},
    "Qendër":   {"pos":(5,4.5), "color":"#FFD93D", "zones":["4.Qendër","7.Jug"]},
    "Lindje":   {"pos":(9,5.5), "color":"#6BCB77", "zones":["2.Lindje","3.LindjeJug","8.JugLindje"]},
}

ZONE_POLYS = {
    "1.Veri":[(19.750,41.380),(19.800,41.405),(19.860,41.440),(19.930,41.460),(19.982,41.432),(19.965,41.390),(19.925,41.362),(19.870,41.355),(19.815,41.360),(19.755,41.373)],
    "2.Lindje":[(19.945,41.372),(19.982,41.432),(19.998,41.445),(20.058,41.425),(20.085,41.388),(20.063,41.350),(20.018,41.332),(19.968,41.337),(19.952,41.350)],
    "3.LindjeJug":[(19.893,41.312),(19.960,41.312),(19.993,41.330),(20.063,41.350),(20.085,41.388),(20.058,41.425),(19.998,41.445),(19.965,41.452),(19.935,41.355),(19.905,41.315)],
    "4.Qendër":[(19.802,41.322),(19.882,41.322),(19.925,41.348),(19.925,41.362),(19.870,41.355),(19.815,41.360),(19.755,41.373),(19.728,41.363),(19.723,41.350),(19.740,41.328),(19.778,41.318)],
    "5.Perëndim":[(19.675,41.393),(19.720,41.410),(19.750,41.380),(19.728,41.363),(19.700,41.360),(19.680,41.330),(19.678,41.312)],
    "6.JugPerëndim":[(19.678,41.312),(19.742,41.307),(19.802,41.312),(19.778,41.318),(19.740,41.328),(19.723,41.350),(19.700,41.360),(19.680,41.330)],
    "7.Jug":[(19.778,41.282),(19.868,41.274),(19.890,41.280),(19.893,41.312),(19.802,41.312),(19.742,41.307),(19.735,41.285),(19.750,41.278)],
    "8.JugLindje":[(19.890,41.280),(19.992,41.274),(20.028,41.297),(20.033,41.313),(19.993,41.330),(19.952,41.350),(19.925,41.340),(19.905,41.315),(19.893,41.312),(19.895,41.297)],
}

CENTROIDS = {
    "1.Veri":        (19.862,41.415),
    "2.Lindje":      (20.010,41.395),
    "3.LindjeJug":   (19.990,41.365),
    "4.Qendër":      (19.828,41.342),
    "5.Perëndim":    (19.708,41.373),
    "6.JugPerëndim": (19.733,41.333),
    "7.Jug":         (19.833,41.290),
    "8.JugLindje":   (19.960,41.300),
}

WH_LONLAT = {
    "Perëndim": (19.750,41.365),
    "Qendër":   (19.870,41.350),
    "Lindje":   (20.010,41.370),
}

# =========================================================
# GRAPH
# =========================================================

def dist(p1, p2):
    return round(math.sqrt((p2[0]-p1[0])**2+(p2[1]-p1[1])**2), 3)

def build_graph():
    G = nx.DiGraph()

    # warehouse + zone nodes
    for wh, d in WAREHOUSES.items():
        G.add_node(wh, kind="wh", pos=d["pos"], color=d["color"])
    for z, d in ZONES.items():
        G.add_node(z, kind="zone", pos=d["pos"], color=d["color"])

    # warehouse → zone edges
    for wh, d in WAREHOUSES.items():
        for z in d["zones"]:
            w = dist(d["pos"], ZONES[z]["pos"])
            G.add_edge(wh, z, weight=w, etype="supply")
            G.add_edge(z, wh, weight=w, etype="return")

    # clients + flower loop per zone
    for z, d in ZONES.items():
        zpos = d["pos"]
        random.seed(hash(z) & 0xFFFF)
        clients = []
        for i in range(16):
            cx = zpos[0] + random.uniform(-1.2, 1.2)
            cy = zpos[1] + random.uniform(-1.2, 1.2)
            cid = f"{z}_K{i+1:02d}"
            G.add_node(cid, kind="client", pos=(cx,cy), color=d["color"], zone=z)
            clients.append(cid)

        # zone → first client
        G.add_edge(z, clients[0], weight=dist(zpos, G.nodes[clients[0]]["pos"]), etype="delivery")

        # flower: client → client (ring)
        for i in range(len(clients)):
            a, b = clients[i], clients[(i+1)%len(clients)]
            G.add_edge(a, b, weight=dist(G.nodes[a]["pos"], G.nodes[b]["pos"]), etype="flower")

        # last client → zone
        G.add_edge(clients[-1], z, weight=dist(G.nodes[clients[-1]]["pos"], zpos), etype="flower_return")

    return G

# =========================================================
# DRAW GRAPH (top)
# =========================================================

ECLR = {
    "supply":        "#6EE7B7",
    "return":        "#A78BFA",
    "delivery":      "#93C5FD",
    "flower":        "#FCD34D",
    "flower_return": "#FB923C",
}

def arrow(ax, p1, p2, color, lw, rad=0.1, alpha=0.9):
    ax.annotate("", xy=p2, xytext=p1,
        arrowprops=dict(arrowstyle="->", color=color, lw=lw,
                        connectionstyle=f"arc3,rad={rad}", alpha=alpha))

def wlabel(ax, p1, p2, w, color):
    mx,my = (p1[0]+p2[0])/2,(p1[1]+p2[1])/2
    dx,dy = p2[0]-p1[0],p2[1]-p1[1]
    L = math.hypot(dx,dy) or 1
    ax.text(mx-dy/L*0.15, my+dx/L*0.15, f"{w:.2f}",
            fontsize=5.5, color=color, ha="center", va="center",
            fontfamily="monospace",
            path_effects=[pe.withStroke(linewidth=1.6, foreground=BG)])

def draw_graph(ax, G):
    ax.set_facecolor(BG)
    pos = nx.get_node_attributes(G, "pos")

    wh_nodes     = [n for n in G if G.nodes[n]["kind"]=="wh"]
    zone_nodes   = [n for n in G if G.nodes[n]["kind"]=="zone"]
    client_nodes = [n for n in G if G.nodes[n]["kind"]=="client"]

    by_type = {}
    for u,v,d in G.edges(data=True):
        t = d["etype"]
        by_type.setdefault(t,[]).append((u,v,d))

    for u,v,d in by_type.get("flower",[]):
        arrow(ax,pos[u],pos[v],ECLR["flower"],0.4,rad=0.08,alpha=0.30)
    for u,v,d in by_type.get("flower_return",[]):
        arrow(ax,pos[u],pos[v],ECLR["flower_return"],0.6,rad=0.12,alpha=0.40)
    for u,v,d in by_type.get("delivery",[]):
        arrow(ax,pos[u],pos[v],ECLR["delivery"],0.9,rad=0.05,alpha=0.60)
    for u,v,d in by_type.get("supply",[]):
        arrow(ax,pos[u],pos[v],ECLR["supply"],1.8,rad=0.15,alpha=0.95)
        wlabel(ax,pos[u],pos[v],d["weight"],ECLR["supply"])
    for u,v,d in by_type.get("return",[]):
        arrow(ax,pos[u],pos[v],ECLR["return"],1.2,rad=0.22,alpha=0.80)
        wlabel(ax,pos[u],pos[v],d["weight"],ECLR["return"])

    nx.draw_networkx_nodes(G,pos,ax=ax,nodelist=client_nodes,node_size=50,
        node_color=[G.nodes[n]["color"] for n in client_nodes],alpha=0.60)
    nx.draw_networkx_nodes(G,pos,ax=ax,nodelist=zone_nodes,node_size=500,
        node_color=[G.nodes[n]["color"] for n in zone_nodes],
        edgecolors="white",linewidths=1.2,alpha=0.95)
    nx.draw_networkx_nodes(G,pos,ax=ax,nodelist=wh_nodes,node_size=900,
        node_color=[G.nodes[n]["color"] for n in wh_nodes],
        edgecolors="white",linewidths=2.0)

    for n in wh_nodes:
        x,y=pos[n]
        ax.text(x,y-0.55,f"Magazina {n}",fontsize=7,color="white",ha="center",
                fontweight="bold",path_effects=[pe.withStroke(linewidth=2,foreground=BG)])
        ax.text(x,y-0.82,"⚙ 2.5 kg",fontsize=6,color="#AAAAAA",ha="center",
                path_effects=[pe.withStroke(linewidth=1.5,foreground=BG)])
    for n in zone_nodes:
        x,y=pos[n]
        ax.text(x,y+0.42,f"{n}\n{ZONES[n]['pct']}",fontsize=6,color="white",
                ha="center",va="bottom",fontweight="bold",multialignment="center",
                path_effects=[pe.withStroke(linewidth=1.8,foreground=BG)])

    handles=[
        Line2D([0],[0],color=ECLR["supply"],lw=2,label="Magazinë→Zonë (supply, weight shown)"),
        Line2D([0],[0],color=ECLR["return"],lw=1.5,label="Zonë→Magazinë (return)",linestyle="--"),
        Line2D([0],[0],color=ECLR["delivery"],lw=1.2,label="Zonë→Klient i parë"),
        Line2D([0],[0],color=ECLR["flower"],lw=1,label="Klient→Klient (flower loop)"),
        Line2D([0],[0],color=ECLR["flower_return"],lw=1,label="Klient i fundit→Zonë"),
        mpatches.Patch(facecolor="#FF6B6B",edgecolor="w",label="Magazinë (2.5kg)"),
        mpatches.Patch(facecolor="#5B9BD5",edgecolor="w",label="Zonë"),
        mpatches.Patch(facecolor="#F4C144",label="Klient (16/zonë)"),
    ]
    ax.legend(handles=handles,loc="lower right",fontsize=7,
              facecolor="#1C2128",edgecolor="#444",labelcolor="white",
              framealpha=0.92,borderpad=0.8,labelspacing=0.4)
    ax.set_title("TIRANA FLY — GRAPH I RRUGËVE TË DRONËVE",
                 fontsize=14,fontweight="bold",color="white",pad=10)
    ax.text(0.01,0.01,"Drone ≥ 2.5 kg  |  Peshat = Distanca Euklidiane",
            transform=ax.transAxes,fontsize=6.5,color="#777",va="bottom")
    ax.set_axis_off()

# =========================================================
# DRAW MAP (bottom)
# =========================================================

def draw_map(ax):
    ax.set_facecolor("#1a2233")

    for zname, coords in ZONE_POLYS.items():
        color = ZONES[zname]["color"]
        ax.add_patch(MplPolygon(coords,closed=True,facecolor=color,
                                edgecolor="white",linewidth=1.0,alpha=0.72,zorder=1))

    # clients on map
    for zname, d in ZONES.items():
        clon,clat = CENTROIDS[zname]
        random.seed(hash(zname) & 0xFFFF)
        lons=[clon+random.uniform(-0.03,0.03) for _ in range(16)]
        lats=[clat+random.uniform(-0.02,0.02) for _ in range(16)]
        ax.scatter(lons,lats,s=10,color=d["color"],alpha=0.90,zorder=3,linewidths=0)

    # drone routes
    for wh, d in WAREHOUSES.items():
        wlon,wlat = WH_LONLAT[wh]
        wc = d["color"]
        for zname in d["zones"]:
            zlon,zlat = CENTROIDS[zname]
            ax.annotate("",xy=(zlon,zlat),xytext=(wlon,wlat),
                arrowprops=dict(arrowstyle="->",color=wc,lw=1.6,
                                connectionstyle="arc3,rad=0.12",alpha=0.95),zorder=4)
            dd = dist((wlon,wlat),(zlon,zlat))
            ax.text((wlon+zlon)/2,(wlat+zlat)/2,f"{dd:.3f}°",
                    fontsize=5,color=wc,ha="center",va="center",
                    path_effects=[pe.withStroke(linewidth=1.2,foreground=BG)])

    # warehouses
    for wh,(wlon,wlat) in WH_LONLAT.items():
        c=WAREHOUSES[wh]["color"]
        ax.plot(wlon,wlat,"s",markersize=12,color=c,
                markeredgecolor="white",markeredgewidth=1.5,zorder=5)
        ax.text(wlon,wlat-0.006,f"Magazina {wh}",fontsize=6,color="white",
                ha="center",va="top",fontweight="bold",zorder=6,
                path_effects=[pe.withStroke(linewidth=1.5,foreground=BG)])

    # zone labels
    for zname,(zlon,zlat) in CENTROIDS.items():
        ax.text(zlon,zlat,zname,fontsize=5.5,color="white",
                ha="center",va="center",fontweight="bold",zorder=6,
                path_effects=[pe.withStroke(linewidth=1.3,foreground="#00000099")])

    ax.set_xlim(19.64,20.11)
    ax.set_ylim(41.26,41.47)
    ax.set_xlabel("Gjerësi (°E)",fontsize=7,color="#888")
    ax.set_ylabel("Lartësi (°N)",fontsize=7,color="#888")
    ax.tick_params(colors="#555",labelsize=6)
    for sp in ax.spines.values(): sp.set_edgecolor("#333")
    ax.set_title("TIRANA FLY — HARTA E ZONAVE",
                 fontsize=12,fontweight="bold",color="white",pad=8)

# =========================================================
# MAIN
# =========================================================

print("Building …")
G = build_graph()
print(f"Nodes: {G.number_of_nodes()}  Edges: {G.number_of_edges()}")

fig = plt.figure(figsize=(20,24), facecolor=BG)
ax1 = fig.add_axes([0.02, 0.40, 0.96, 0.57])
ax2 = fig.add_axes([0.02, 0.01, 0.96, 0.37])

draw_graph(ax1, G)
draw_map(ax2)

fig.add_artist(plt.Line2D([0.02,0.98],[0.395,0.395],
               color="#444",linewidth=1,transform=fig.transFigure))

print("Showing … (close the window when done)")
plt.show()
