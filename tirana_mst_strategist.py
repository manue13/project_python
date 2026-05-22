# =====================================================================
# tirana_mst_strategist.py
# STUDENT 3: THE FLEET STRATEGIST — INDEPENDENT MST & CAPACITY CORE
# =====================================================================

import networkx as nx
import random
import matplotlib.pyplot as plt

# Safely import the map data foundations from Student 1 and Student 2
from tirana_data import generate_all_clients
from tirana_graph_builder import build_graph
from tirana_multi_delivery import (
    make_graph_bidirectional, 
    graph_to_adj, 
    route_distance
)

# =====================================================================
# DISJOINT SET (UNION-FIND) DATA STRUCTURE FOR KRUSKAL'S
# =====================================================================

def find_parent_mst(parent_array, node):
    if parent_array[node] == node:
        return node
    parent_array[node] = find_parent_mst(parent_array, parent_array[node])
    return parent_array[node]

def union_nodes_mst(parent_array, rank_array, root_x, root_y):
    if rank_array[root_x] < rank_array[root_y]:
        parent_array[root_x] = root_y
    elif rank_array[root_x] > rank_array[root_y]:
        parent_array[root_y] = root_x
    else:
        parent_array[root_y] = root_x
        rank_array[root_x] += 1

# =====================================================================
# UNCONSTRAINED FLEET ROUTING ALGORITHM (STUDENT 3 ROLE)
# =====================================================================

def create_unconstrained_strategist_trips(G, adj, depot, clients, package_weights):
    """
    Builds realistic drone delivery loops based strictly on payload capacity (5kg),
    completely unconstrained by battery caps as mandated for Student 3.
    """
    # Group clients into 3 balanced workloads to naturally use all 3 drones
    random.seed(42)
    sorted_clients = sorted(clients, key=lambda c: package_weights[c], reverse=True)
    
    drone_trips = []
    # Explicitly assign chunks to Drones 1, 2, and 3
    chunks = [[] for _ in range(3)]
    for idx, client in enumerate(sorted_clients):
        chunks[idx % 3].append(client)
        
    for drone_id, client_chunk in enumerate(chunks, start=1):
        if not client_chunk:
            continue
            
        current_path = [depot]
        current_weight = 0.0
        current_dist = 0.0
        
        for client in client_chunk:
            weight = package_weights[client]
            # Real-world payload cap constraint check (5.0 kg)
            if current_weight + weight <= 5.0:
                # Add path distance from last stop to this client
                step_dist = route_distance(adj, [current_path[-1], client])[0]
                current_dist += step_dist
                current_path.append(client)
                current_weight += weight
            else:
                # Payload full: return to depot and start a new trip loop
                step_dist = route_distance(adj, [current_path[-1], depot])[0]
                current_dist += step_dist
                current_path.append(depot)
                drone_trips.append({"drone": drone_id, "path": current_path, "distance": current_dist})
                
                # Start next trip immediately
                step_dist = route_distance(adj, [depot, client])[0]
                current_path = [depot, client]
                current_weight = weight
                current_dist = step_dist
                
        # Always return the drone back to the central depot at the very end
        if current_path[-1] != depot:
            step_dist = route_distance(adj, [current_path[-1], depot])[0]
            current_dist += step_dist
            current_path.append(depot)
            drone_trips.append({"drone": drone_id, "path": current_path, "distance": current_dist})
            
    return drone_trips

# =====================================================================
# CORE MST ENGINE & MAIN VISUALIZER
# =====================================================================

def run_student3_mst_analysis(G, adj, depot, clients, dynamic_trips):
    print("\n" + "="*25 + " STUDENT 3: MST ANALYSIS " + "="*25)
    
    network_nodes = [depot] + clients
    node_to_idx = {node: i for i, node in enumerate(network_nodes)}
    node_positions = {node: G.nodes[node]["pos"] for node in network_nodes}
    
    # 1. Compute all pair-wise shortest paths using Student 2's Dijkstra foundation
    all_possible_edges = []
    for i in range(len(network_nodes)):
        for j in range(i + 1, len(network_nodes)):
            u, v = network_nodes[i], network_nodes[j]
            dist = route_distance(adj, [u, v])[0]
            all_possible_edges.append((dist, u, v))
            
    # 2. Kruskal's Core Phase: Sort all edges by distance (Greedy Choice)
    all_possible_edges.sort(key=lambda x: x[0])
    
    parent = [i for i in range(len(network_nodes))]
    rank = [0] * len(network_nodes)
    
    mst_edges = []
    total_mst_backbone_distance = 0.0
    
    # 3. Kruskal's Selection Loop (Cycle Prevention)
    for edge_weight, u, v in all_possible_edges:
        root_u = find_parent_mst(parent, node_to_idx[u])
        root_v = find_parent_mst(parent, node_to_idx[v])
        
        if root_u != root_v:
            mst_edges.append((u, v, edge_weight))
            total_mst_backbone_distance += edge_weight
            union_nodes_mst(parent, rank, root_u, root_v)
            
    total_batch_delivery_distance = sum(trip["distance"] for trip in dynamic_trips)

    # Print clean diagnostic metrics
    print(f"[Kruskal's Engine] Connected {len(network_nodes)} nodes using an optimal structural spine.")
    print(f"-> Total Minimum Spanning Tree Backbone Distance: {total_mst_backbone_distance:.2f} km")
    print(f"-> Total Realized Multi-Trip Drone Batch Distance: {total_batch_delivery_distance:.2f} km")
    
    print("\n" + "="*19 + " OPTIMIZATION COMPARISON ANALYSIS " + "="*19)
    print("Why the Batch Delivery Route exceeds the structural MST Backbone lower bound:")
    print("1. Capacity Restrictions : Packages are strictly limited to MAX_WEIGHT = 5.0 kg.")
    print("2. Battery Assertions    : Battery ranges are treated as unconstrained per Student 3 spec.")
    print("3. Cyclical Redundancy   : Drones must return to the Depot after drop-offs, adding loops.")
    print("=" * 65)
    
    # =====================================================================
    # SIDE-BY-SIDE EVALUATION PLOTTER
    # =====================================================================
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6.5))
    fig.suptitle("TiranaFly - Optimization & Infrastructure Assessment", fontsize=14, fontweight='bold', color='black')
    
    for ax in (ax1, ax2):
        ax.set_facecolor('white')
        ax.grid(True, linestyle='--', alpha=0.5, color='lightblue')
        ax.set_xlabel("Graph Coordinate X", fontsize=9, color='darkblue')
        ax.set_ylabel("Graph Coordinate Y", fontsize=9, color='darkblue')

    # ---- LEFT PLOT: STRUCTURAL MST BACKBONE ----
    ax1.set_title(f"Structural MST Spine Lower Bound\nTotal Length: {total_mst_backbone_distance:.2f} km", fontsize=11, fontweight='bold', color='black')
    for u, v, w in mst_edges:
        x_coords = [node_positions[u][0], node_positions[v][0]]
        y_coords = [node_positions[u][1], node_positions[v][1]]
        ax1.plot(x_coords, y_coords, color='blue', linewidth=2.5, zorder=1, label='MST Backbone Link' if 'MST Backbone Link' not in ax1.get_legend_handles_labels()[1] else '')
        
    # ---- RIGHT PLOT: UNCONSTRAINED 3-DRONE OPERATIONS ----
    ax2.set_title(f"Realized Operational Fleet Routes (CVRP)\nTotal Fleet Length: {total_batch_delivery_distance:.2f} km", fontsize=11, fontweight='bold', color='black')
    
    drone_colors = {1: 'red', 2: 'green', 3: 'orange'}
    drone_labels = {1: 'Drone 1 (Red Link)', 2: 'Drone 2 (Green Link)', 3: 'Drone 3 (Orange Link)'}
    
    for trip in dynamic_trips:
        d_id = trip["drone"]
        path_nodes = trip["path"]
        color = drone_colors.get(d_id, 'grey')
        label = drone_labels.get(d_id, f'Drone {d_id} Route')
        
        for k in range(len(path_nodes) - 1):
            u, v = path_nodes[k], path_nodes[k+1]
            x_coords = [G.nodes[u]["pos"][0], G.nodes[v]["pos"][0]]
            y_coords = [G.nodes[u]["pos"][1], G.nodes[v]["pos"][1]]
            ax2.plot(x_coords, y_coords, color=color, linewidth=2.2, zorder=1, label=label if label not in ax2.get_legend_handles_labels()[1] else '')

    # Overlay Depot and Client layouts
    for ax in (ax1, ax2):
        client_x = [pos[0] for node, pos in node_positions.items() if node != depot]
        client_y = [pos[1] for node, pos in node_positions.items() if node != depot]
        ax.scatter(client_x, client_y, color='darkgrey', s=120, edgecolor='black', zorder=3, label='Client Nodes')
        
        ax.scatter(node_positions[depot][0], node_positions[depot][1], color='pink', s=250, marker='H', edgecolor='black', zorder=4, label='Central Depot')
        ax.text(node_positions[depot][0], node_positions[depot][1] + 0.25, "DEPOT", fontsize=8, fontweight='bold', ha='center', color='purple')
        ax.legend(loc='upper right', fontsize=8)

    plt.tight_layout()
    print("\n[Visualizer Window] Rendering comparison layouts. Close plot window to complete execution.")
    plt.show()

# =====================================================================
# RUNNER BLOCK
# =====================================================================

if __name__ == "__main__":
    random.seed(42)
    
    G_directed = build_graph(16)
    G = make_graph_bidirectional(G_directed)
    adj = graph_to_adj(G)
    
    selected_zone = "1. Veri"
    depot = "Magazina Perëndim"
    
    all_zone_clients = generate_all_clients(16)
    clients = [c["id"] for c in all_zone_clients[selected_zone]]
    
    package_weights = {c: round(random.uniform(0.45, 0.75), 2) for c in clients}
    
    # Calculate unconstrained fleet loops specifically matching Student 3 requirements
    unconstrained_trips = create_unconstrained_strategist_trips(G, adj, depot, clients, package_weights)
            
    # Run analysis
    run_student3_mst_analysis(G, adj, depot, clients, unconstrained_trips)