# =========================================================
# TIRANA FLY — FINAL VERSION
#
# Goal:
# 3 drones for one zone must visit all 16 clients.
#
# Rules:
# - Each drone starts from the warehouse/depot.
# - Each drone carries packages up to 5 kg.
# - Each drone travels maximum 15 km.
# - The 16 clients are divided between the 3 drones.
# - For each drone, the shortest route is calculated using Dijkstra.
# - Drone 1 finishes and returns, then Drone 2 starts, then Drone 3.
# - The drone is animated on the map.
# =========================================================

import heapq
import random
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import networkx as nx

from tirana_graph_builder import build_graph


# =========================================================
# CONSTRAINTS
# =========================================================

MAX_DISTANCE = 15.0
MAX_WEIGHT = 5.0
TOTAL_CLIENTS = 16
DRONES_PER_ZONE = 3

# IMPORTANT:
# Your graph coordinates are not real kilometers.
# This factor converts graph distance units into approximate km.
# If routes still pass 15 km, lower this to 0.35.
KM_PER_GRAPH_UNIT = 0.40


# =========================================================
# MAKE GRAPH BIDIRECTIONAL
# =========================================================

def make_graph_bidirectional(G):
    edges_to_add = []

    for u, v, data in G.edges(data=True):
        if not G.has_edge(v, u):
            edges_to_add.append((v, u, data["weight"]))

    for u, v, weight in edges_to_add:
        G.add_edge(u, v, weight=weight, edge_type="reverse")

    return G


# =========================================================
# GRAPH TO ADJACENCY LIST
# =========================================================

def graph_to_adj(G):
    adj = {}

    for node in G.nodes:
        adj[node] = []

    for u, v, data in G.edges(data=True):
        weight_in_km = data["weight"] * KM_PER_GRAPH_UNIT
        adj[u].append((v, weight_in_km))

    return adj


# =========================================================
# DIJKSTRA ALGORITHM
# =========================================================

def dijkstra(adj, start, end):
    distances = {}
    parents = {}

    for node in adj:
        distances[node] = float("inf")
        parents[node] = None

    distances[start] = 0

    pq = []
    heapq.heappush(pq, (0, start))

    visited = set()

    while pq:
        current_distance, current_node = heapq.heappop(pq)

        if current_node in visited:
            continue

        visited.add(current_node)

        if current_node == end:
            break

        for neighbor, weight in adj[current_node]:
            new_distance = current_distance + weight

            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                parents[neighbor] = current_node
                heapq.heappush(pq, (new_distance, neighbor))

    path = []
    node = end

    while node is not None:
        path.append(node)
        node = parents[node]

    path.reverse()

    if len(path) == 0 or path[0] != start:
        return float("inf"), []

    return round(distances[end], 3), path


# =========================================================
# ROUTE DISTANCE USING DIJKSTRA
# =========================================================

def route_distance(adj, route_nodes):
    total_distance = 0
    full_path = []

    for i in range(len(route_nodes) - 1):
        start = route_nodes[i]
        end = route_nodes[i + 1]

        distance, path = dijkstra(adj, start, end)

        if path == []:
            return float("inf"), []

        total_distance += distance

        if i == 0:
            full_path.extend(path)
        else:
            full_path.extend(path[1:])

    return round(total_distance, 3), full_path


# =========================================================
# HELPERS
# =========================================================

def get_depots(G):
    depots = []

    for node, data in G.nodes(data=True):
        if data.get("node_type") == "warehouse":
            depots.append(node)

    return depots


def get_zones_for_depot(G, depot):
    zones = []

    for neighbor in G.successors(depot):
        if G.nodes[neighbor].get("node_type") == "zone":
            zones.append(neighbor)

    return zones


def get_16_clients_for_zone(G, zone):
    clients = []

    for node, data in G.nodes(data=True):
        if data.get("node_type") == "client" and data.get("zone") == zone:
            clients.append(node)

    return clients[:TOTAL_CLIENTS]


# =========================================================
# PACKAGE WEIGHTS
# =========================================================

def assign_package_weights(clients):
    """
    Weights are chosen so that 3 drones can carry all 16 packages.
    Total per drone must stay under 5 kg.
    """

    random.seed(10)

    package_weights = {}

    for client in clients:
        package_weights[client] = round(random.uniform(0.45, 0.75), 2)

    return package_weights


# =========================================================
# SHORTEST ORDER FOR A GROUP OF CLIENTS
# =========================================================

def find_best_insertion(adj, depot, current_clients, new_client):
    best_order = None
    best_distance = float("inf")
    best_path = []

    for position in range(len(current_clients) + 1):
        test_order = current_clients.copy()
        test_order.insert(position, new_client)

        route_nodes = [depot] + test_order + [depot]

        distance, path = route_distance(adj, route_nodes)

        if distance < best_distance:
            best_distance = distance
            best_order = test_order
            best_path = path

    return best_order, best_distance, best_path


def shortest_route_for_group(adj, depot, client_group):
    """
    Builds a short route for one drone using insertion.
    It still uses Dijkstra between every pair of nodes.
    """

    selected_clients = []
    final_distance = 0
    final_path = []

    for client in client_group:
        order, distance, path = find_best_insertion(
            adj,
            depot,
            selected_clients,
            client
        )

        selected_clients = order
        final_distance = distance
        final_path = path

    return selected_clients, final_distance, final_path


# =========================================================
# DISTRIBUTE 16 CLIENTS INTO 3 DRONES
# =========================================================

def create_drone_trips(G, depot, clients, package_weights):
    """
    This version guarantees that the algorithm tries to assign
    all 16 clients to exactly 3 drones.

    Distribution:
    - Drone 1 gets clients until close to 5 kg
    - Drone 2 gets clients until close to 5 kg
    - Drone 3 gets the remaining clients

    Then the shortest route for each drone is calculated.
    """

    adj = graph_to_adj(G)

    unserved_clients = clients.copy()
    trips = []

    for drone_number in range(1, DRONES_PER_ZONE + 1):
        selected_clients = []
        current_weight = 0

        drones_left_after_this = DRONES_PER_ZONE - drone_number

        for client in unserved_clients.copy():
            client_weight = package_weights[client]

            # For drone 3, try to take all remaining clients if possible
            if drone_number == DRONES_PER_ZONE:
                if current_weight + client_weight <= MAX_WEIGHT:
                    selected_clients.append(client)
                    current_weight += client_weight
                    unserved_clients.remove(client)

            # For drone 1 and 2, leave enough clients for the next drones
            else:
                remaining_after_take = len(unserved_clients) - 1
                minimum_clients_to_leave = drones_left_after_this

                if remaining_after_take < minimum_clients_to_leave:
                    continue

                if current_weight + client_weight <= MAX_WEIGHT:
                    selected_clients.append(client)
                    current_weight += client_weight
                    unserved_clients.remove(client)

        if len(selected_clients) == 0:
            continue

        final_order, final_distance, final_path = shortest_route_for_group(
            adj,
            depot,
            selected_clients
        )

        trips.append({
            "drone": drone_number,
            "clients": final_order,
            "weight": round(current_weight, 2),
            "distance": final_distance,
            "path": final_path,
            "feasible_distance": final_distance <= MAX_DISTANCE,
            "feasible_weight": current_weight <= MAX_WEIGHT
        })

    return trips, unserved_clients


# =========================================================
# DRAW BACKGROUND
# =========================================================

def draw_background(G, depot, selected_zone, clients, package_weights):
    pos = nx.get_node_attributes(G, "pos")

    fig, ax = plt.subplots(figsize=(14, 9))

    ax.set_title(
        "TiranaFly — 3 Drones Visit All 16 Clients",
        fontsize=15,
        fontweight="bold"
    )

    nx.draw_networkx_edges(
        G,
        pos,
        ax=ax,
        alpha=0.12,
        arrows=True,
        arrowsize=7
    )

    warehouses = []
    zones = []
    all_clients = []

    for node, data in G.nodes(data=True):
        if data.get("node_type") == "warehouse":
            warehouses.append(node)
        elif data.get("node_type") == "zone":
            zones.append(node)
        elif data.get("node_type") == "client":
            all_clients.append(node)

    nx.draw_networkx_nodes(
        G,
        pos,
        nodelist=warehouses,
        node_size=900,
        node_shape="s",
        node_color="orange",
        edgecolors="black",
        ax=ax
    )

    nx.draw_networkx_nodes(
        G,
        pos,
        nodelist=zones,
        node_size=500,
        node_color="lightblue",
        edgecolors="black",
        ax=ax
    )

    nx.draw_networkx_nodes(
        G,
        pos,
        nodelist=all_clients,
        node_size=55,
        node_color="lightgray",
        ax=ax
    )

    nx.draw_networkx_nodes(
        G,
        pos,
        nodelist=clients,
        node_size=180,
        node_color="lime",
        edgecolors="black",
        ax=ax
    )

    nx.draw_networkx_nodes(
        G,
        pos,
        nodelist=[depot],
        node_size=1300,
        node_shape="s",
        node_color="gold",
        edgecolors="red",
        linewidths=3,
        ax=ax
    )

    nx.draw_networkx_nodes(
        G,
        pos,
        nodelist=[selected_zone],
        node_size=750,
        node_color="deepskyblue",
        edgecolors="black",
        linewidths=3,
        ax=ax
    )

    labels = {}

    for node in warehouses + zones:
        labels[node] = node

    for i, client in enumerate(clients, start=1):
        labels[client] = f"C{i}\n{package_weights[client]}kg"

    nx.draw_networkx_labels(
        G,
        pos,
        labels=labels,
        font_size=8,
        ax=ax
    )

    ax.axis("off")

    return fig, ax, pos


# =========================================================
# ANIMATION POINTS
# =========================================================

def build_animation_points(G, trips):
    pos = nx.get_node_attributes(G, "pos")

    animation_points = []

    for trip in trips:
        path = trip["path"]

        for i in range(len(path) - 1):
            current_node = path[i]
            next_node = path[i + 1]

            x1, y1 = pos[current_node]
            x2, y2 = pos[next_node]

            steps = 35

            for step in range(steps + 1):
                t = step / steps

                x = x1 + (x2 - x1) * t
                y = y1 + (y2 - y1) * t

                animation_points.append({
                    "x": x,
                    "y": y,
                    "from": current_node,
                    "to": next_node,
                    "drone": trip["drone"],
                    "distance": trip["distance"],
                    "weight": trip["weight"],
                    "clients": trip["clients"]
                })

    return animation_points


# =========================================================
# ANIMATE DRONES
# =========================================================

def animate_all_drones(G, depot, selected_zone, clients, package_weights, trips):
    fig, ax, pos = draw_background(
        G,
        depot,
        selected_zone,
        clients,
        package_weights
    )

    animation_points = build_animation_points(G, trips)

    if len(animation_points) == 0:
        print("No animation points found.")
        plt.show()
        return

    drone_object = ax.scatter(
        animation_points[0]["x"],
        animation_points[0]["y"],
        s=550,
        marker="^",
        color="red",
        edgecolor="black",
        linewidth=1.5,
        zorder=20
    )

    drone_label = ax.text(
        animation_points[0]["x"],
        animation_points[0]["y"] + 0.25,
        "DRONE 1",
        fontsize=9,
        fontweight="bold",
        color="red",
        ha="center",
        zorder=21
    )

    route_x = []
    route_y = []

    route_line, = ax.plot(
        [],
        [],
        color="red",
        linewidth=3,
        zorder=15
    )

    info_text = ax.text(
        0.02,
        0.02,
        "",
        transform=ax.transAxes,
        fontsize=11,
        bbox=dict(facecolor="white", alpha=0.85),
        zorder=30
    )

    last_drone = animation_points[0]["drone"]

    def update(frame):
        nonlocal last_drone, route_x, route_y

        point = animation_points[frame]

        if point["drone"] != last_drone:
            route_x = []
            route_y = []
            last_drone = point["drone"]

        x = point["x"]
        y = point["y"]

        drone_object.set_offsets([[x, y]])
        drone_label.set_position((x, y + 0.25))
        drone_label.set_text(f"DRONE {point['drone']}")

        route_x.append(x)
        route_y.append(y)
        route_line.set_data(route_x, route_y)

        client_names = ", ".join(point["clients"])

        info_text.set_text(
            f"Drone {point['drone']} moving:\n"
            f"{point['from']} -> {point['to']}\n"
            f"Distance: {point['distance']} km / {MAX_DISTANCE} km\n"
            f"Weight: {point['weight']} kg / {MAX_WEIGHT} kg\n"
            f"Clients served: {len(point['clients'])}\n"
            f"{client_names}"
        )

        return drone_object, drone_label, route_line, info_text

    animation = FuncAnimation(
        fig,
        update,
        frames=len(animation_points),
        interval=35,
        repeat=False,
        blit=False
    )

    fig.animation = animation
    fig.canvas.draw()
    plt.show()


# =========================================================
# MAIN PROGRAM
# =========================================================

if __name__ == "__main__":
    G = build_graph(clients_per_zone=16)
    G = make_graph_bidirectional(G)

    depots = get_depots(G)

    print("\nAvailable depots:")

    for i, depot in enumerate(depots, start=1):
        print(f"{i}. {depot}")

    depot_choice = input("\nChoose depot number: ")

    try:
        depot = depots[int(depot_choice) - 1]
    except:
        depot = depots[0]
        print("Invalid choice. Default depot selected:", depot)

    zones = get_zones_for_depot(G, depot)

    print("\nZones supplied by this depot:")

    for i, zone in enumerate(zones, start=1):
        print(f"{i}. {zone}")

    zone_choice = input("\nChoose zone number with 16 clients: ")

    try:
        selected_zone = zones[int(zone_choice) - 1]
    except:
        selected_zone = zones[0]
        print("Invalid choice. Default zone selected:", selected_zone)

    clients = get_16_clients_for_zone(G, selected_zone)
    package_weights = assign_package_weights(clients)

    print("\n================ SELECTED DATA ================")
    print("Depot:", depot)
    print("Zone:", selected_zone)
    print("Total clients in this zone:", len(clients))
    print("Drones available:", DRONES_PER_ZONE)

    print("\n================ CLIENT PACKAGES ================")

    for i, client in enumerate(clients, start=1):
        print(f"C{i}: {client} | package = {package_weights[client]} kg")

    trips, unserved_clients = create_drone_trips(
        G,
        depot,
        clients,
        package_weights
    )

    print("\n================ DRONE TRIPS ================")

    served_clients = 0

    for trip in trips:
        served_clients += len(trip["clients"])

        print(f"\nDrone {trip['drone']}")
        print("Clients:", trip["clients"])
        print("Number of clients:", len(trip["clients"]))
        print("Total weight:", trip["weight"], "kg")
        print("Total distance:", trip["distance"], "km")
        print("Distance feasible:", trip["feasible_distance"])
        print("Weight feasible:", trip["feasible_weight"])
        print("Path:")
        print(" -> ".join(trip["path"]))

    print("\n================ SUMMARY ================")
    print("Total clients in this zone:", len(clients))
    print("Clients served:", served_clients)
    print("Clients not served:", len(unserved_clients))
    print("Total drones used:", len(trips), "/", DRONES_PER_ZONE)
    print("Max weight per drone:", MAX_WEIGHT, "kg")
    print("Max distance per drone:", MAX_DISTANCE, "km")

    if served_clients == 16:
        print("\nSUCCESS: All 16 clients were visited by the 3 drones.")
    else:
        print("\nWARNING: Not all clients were visited.")

    animate_all_drones(
        G,
        depot,
        selected_zone,
        clients,
        package_weights,
        trips
    )