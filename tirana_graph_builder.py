# =========================================================
# TIRANA FLY — GRAPH BUILDER
# Builds a NetworkX graph ready for Dijkstra (later).
#
# Node types:
#   "warehouse"  — 3 warehouse hubs
#   "zone"       — 8 delivery zones
#   "client"     — 16+ clients per zone
#
# Edge types & weights (all Euclidean distances):
#   warehouse → zone     (supply connection)
#   zone      → client   (zone–client connection)
#   client    → client   (flower-petal route within zone)
#
# Drone constraint stored on every client node:
#   drone_capacity = 2.5  (kg)
# =========================================================

import networkx as nx
from tirana_data import ZONES, WAREHOUSES, euclidean, generate_all_clients

DRONE_CAPACITY_KG = 2.5


def build_graph(clients_per_zone: int = 16) -> nx.DiGraph:
    """
    Returns a directed graph.
    Direction: warehouse → zone → clients (flower loop back to zone).
    All edge weights = Euclidean distance between node positions.
    """

    G = nx.DiGraph()

    all_clients = generate_all_clients(clients_per_zone)

    # --------------------------------------------------
    # ADD WAREHOUSE NODES
    # --------------------------------------------------
    for wh_name, wh_data in WAREHOUSES.items():
        G.add_node(
            wh_name,
            node_type  = "warehouse",
            pos        = wh_data["pos"],
            color      = wh_data["color"],
        )

    # --------------------------------------------------
    # ADD ZONE NODES + WAREHOUSE→ZONE EDGES
    # --------------------------------------------------
    for zone_name, zone_data in ZONES.items():
        G.add_node(
            zone_name,
            node_type  = "zone",
            pos        = zone_data["pos"],
            color      = zone_data["color"],
            label      = zone_data["label"],
            pct        = zone_data["pct"],
            warehouse  = zone_data["warehouse"],
        )

        wh_pos   = WAREHOUSES[zone_data["warehouse"]]["pos"]
        zone_pos = zone_data["pos"]
        dist     = euclidean(wh_pos, zone_pos)

        # warehouse → zone (and reverse for Dijkstra return path)
        G.add_edge(
            zone_data["warehouse"], zone_name,
            weight    = dist,
            edge_type = "supply",
        )
        G.add_edge(
            zone_name, zone_data["warehouse"],
            weight    = dist,
            edge_type = "return",
        )

    # --------------------------------------------------
    # ADD CLIENT NODES + ZONE→CLIENT + FLOWER EDGES
    # --------------------------------------------------
    for zone_name, clients in all_clients.items():
        zone_pos = ZONES[zone_name]["pos"]

        # zone → first client (entry)
        first_id = clients[0]["id"]
        G.add_node(
            first_id,
            node_type       = "client",
            pos             = clients[0]["pos"],
            zone            = zone_name,
            drone_capacity  = DRONE_CAPACITY_KG,
        )
        d_entry = euclidean(zone_pos, clients[0]["pos"])
        G.add_edge(
            zone_name, first_id,
            weight    = d_entry,
            edge_type = "delivery",
        )

        # flower petal: client[i] → client[i+1]
        for i in range(len(clients)):
            cid = clients[i]["id"]
            if cid not in G:
                G.add_node(
                    cid,
                    node_type      = "client",
                    pos            = clients[i]["pos"],
                    zone           = zone_name,
                    drone_capacity = DRONE_CAPACITY_KG,
                )

            next_i = (i + 1) % len(clients)
            next_id = clients[next_i]["id"]
            if next_id not in G:
                G.add_node(
                    next_id,
                    node_type      = "client",
                    pos            = clients[next_i]["pos"],
                    zone           = zone_name,
                    drone_capacity = DRONE_CAPACITY_KG,
                )

            d = euclidean(clients[i]["pos"], clients[next_i]["pos"])
            G.add_edge(
                cid, next_id,
                weight    = d,
                edge_type = "flower",
            )

        # last client → zone (return petal closes the flower)
        last_id = clients[-1]["id"]
        d_exit = euclidean(clients[-1]["pos"], zone_pos)
        G.add_edge(
            last_id, zone_name,
            weight    = d_exit,
            edge_type = "flower_return",
        )

    return G


def graph_summary(G: nx.DiGraph) -> None:
    print(f"  Nodes  : {G.number_of_nodes()}")
    print(f"  Edges  : {G.number_of_edges()}")
    by_type = {}
    for _, _, d in G.edges(data=True):
        t = d.get("edge_type", "?")
        by_type[t] = by_type.get(t, 0) + 1
    for t, c in sorted(by_type.items()):
        print(f"  [{t}] : {c} edges")
