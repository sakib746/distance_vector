import networkx as nx
import matplotlib.pyplot as plt

def draw_network(net):
    G = nx.Graph()

    # Add nodes (routers)
    for router_name in net.routers:
        G.add_node(router_name)

    # Add edges with weights
    added_edges = set()
    for router_name, router in net.routers.items():
        for neighbor, cost in router.neighbors.items():
            if (neighbor, router_name) not in added_edges:  # avoid double adding
                G.add_edge(router_name, neighbor, weight=cost)
                added_edges.add((router_name, neighbor))


    DG = nx.DiGraph()  # Directed graph for routing paths

# Add next-hop arrows for each destination
    for router_name, router in net.routers.items():
        for dest, (next_hop, cost) in router.routing_table.items():
            if dest != router_name:
                DG.add_edge(router_name, next_hop, color='red')


    pos = nx.spring_layout(G, seed=42)  # nice-looking layout

    # Draw nodes and labels
    nx.draw_networkx_nodes(G, pos, node_color='skyblue', node_size=1500, edgecolors='black')
    nx.draw_networkx_labels(G, pos, font_size=14, font_weight='bold')

    # Draw edges and weights
    nx.draw_networkx_edges(G, pos, width=2)
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=12)

    #draw routing arrows from routing table
    nx.draw_networkx_edges(DG, pos, edge_color='red', arrows=True, connectionstyle='arc3,rad=0.2', width=2)

    plt.title("Distance Vector Routing Network Topology", fontsize=16)
    plt.axis('off')
    plt.tight_layout()
    plt.show()





class Router:
    def __init__(self, name):
        self.name = name
        self.neighbors = {}  # neighbor: cost
        self.routing_table = {name: (name, 0)}  # destination: (next_hop, cost)

    def add_neighbor(self, neighbor, cost):
        self.neighbors[neighbor] = cost
        self.routing_table[neighbor] = (neighbor, cost)

    def send_distance_vector(self):
        """Prepare distance vector for sharing with neighbors."""
        return {dest: (next_hop, cost) for dest, (next_hop, cost) in self.routing_table.items()}

    def update_table(self, from_neighbor, neighbor_vector, cost_to_neighbor):
        updated = False
        for dest in neighbor_vector:
            if dest == self.name:
                continue
            new_cost = neighbor_vector[dest][1] + cost_to_neighbor
            if dest not in self.routing_table or new_cost < self.routing_table[dest][1]:
                self.routing_table[dest] = (from_neighbor, new_cost)
                updated = True
        return updated


class Network:
    def __init__(self):
        self.routers = {}

    def add_router(self, name):
        self.routers[name] = Router(name)

    def connect_routers(self, r1, r2, cost):
        self.routers[r1].add_neighbor(r2, cost)
        self.routers[r2].add_neighbor(r1, cost)

    def run_distance_vector_protocol(self):
        changed = True
        cycle = 0
        while changed:
            print(f"\n--- Cycle {cycle} ---")
            changed = False
            for router_name in self.routers:
                router = self.routers[router_name]
                for neighbor in router.neighbors:
                    neighbor_router = self.routers[neighbor]
                    vector = neighbor_router.send_distance_vector()
                    if router.update_table(neighbor, vector, router.neighbors[neighbor]):
                        changed = True
            cycle += 1

    def print_routing_tables(self):
        for name, router in self.routers.items():
            print(f"\nRouting table for Router {name}:")
            for dest in sorted(router.routing_table):
                next_hop, cost = router.routing_table[dest]
                print(f"  Destination: {dest}, Next Hop: {next_hop}, Cost: {cost}")


# Setup the network topology
net = Network()
for name in ['A', 'B', 'C', 'D']:
    net.add_router(name)

net.connect_routers('A', 'B', 1)
net.connect_routers('A', 'C', 1)
net.connect_routers('B', 'C', 1)
net.connect_routers('B', 'D', 2)
net.connect_routers('C', 'D', 2)

# Run the simulation
net.run_distance_vector_protocol()
net.print_routing_tables()

# Call the function to visualise the simulation
draw_network(net)
