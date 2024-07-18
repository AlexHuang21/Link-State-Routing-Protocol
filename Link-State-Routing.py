import json
import socket
import threading
import time
import sys

class Router:
    def __init__(self, router_id, port, neighbors):
        self.router_id = router_id
        self.port = port
        self.neighbors = neighbors  # Dictionary with neighbor_id: (cost, port)
        self.link_state_database = {}  # router_id: {neighbor_id: cost}
        self.socket = None
        self.routing_table = {}
        self.active = True
        self.sequence_number = 0
        self.received_lsp_info = {}
        self.last_heartbeat_received = {}  # Track the last heartbeat from each neighbor


    def initialize_link_state_database(self):
        # Ensure the database for the router exists
        if self.router_id not in self.link_state_database:
            self.link_state_database[self.router_id] = {}
        # Add each neighbor and its cost to the router's entry in the link state database
        for neighbor, (cost, _) in self.neighbors.items():
            self.link_state_database[self.router_id][neighbor] = cost

    def create_lsp(self):
        self.sequence_number += 1
        lsp = {
            'router_id': self.router_id,
            'neighbors': self.neighbors,
            'sequence_number': self.sequence_number,
            'timestamp': time.time()
        }
        return lsp

    def send_lsp_to_neighbors(self):
        lsp = self.create_lsp()
        lsp_data = json.dumps(lsp).encode('utf-8')  # Encode LSP as JSON
        for neighbor_id, (_, port) in self.neighbors.items():
            if port != self.port:  # Ensure not sending to self
                self.socket.sendto(lsp_data, ('localhost', port))  # Send LSP to neighbor
                # Update the last heartbeat sent timestamp for each neighbor
                self.last_heartbeat_received[neighbor_id] = time.time()
                #print(f"Router {self.router_id}: Sending LSP to Neighbor {neighbor_id} at port {port}")
                #print(lsp)


    def initialize_socket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('127.0.0.1', int(sys.argv[2])))  # Bind to the given port and all interfaces


    def listen_for_lsp(self):
        try:
            lsp_data, addr = self.socket.recvfrom(1024)  # Buffer size is 1024 bytes
            lsp = json.loads(lsp_data.decode('utf-8'))
            sender_id = lsp['router_id']
            sequence_number = lsp['sequence_number']

            # Update heartbeat timestamp for the sender
            self.last_heartbeat_received[sender_id] = time.time()

            if sender_id not in self.neighbors:
                # Handle the case where a node rejoins the network
                #print(f"Router {self.router_id}: Node {sender_id} has rejoined the network.")
                self.neighbors[sender_id] = (lsp['neighbors'][self.router_id], addr[1])  # Update neighbors with cost and port
                # You might need to initiate other reintegration processes here

            # Check if the LSP is new or more recent
            if (sender_id, sequence_number) not in self.received_lsp_info or \
                    self.received_lsp_info[(sender_id, sequence_number)] < lsp['timestamp']:
                self.received_lsp_info[(sender_id, sequence_number)] = lsp['timestamp']
                if sender_id != self.router_id and self.update_link_state_database(lsp, addr):  # update topology and if it updated, rebroadcast to all neighbors except sender
                    self.rebroadcast_lsp(lsp, addr)
        except BlockingIOError:
            # No data received, non-blocking mode will not wait for data
            pass

    def update_link_state_database(self, lsp, sender_addr):
        sender_id = lsp['router_id']
        updated = False
        for neighbor_id, (cost, _) in lsp['neighbors'].items():
            if neighbor_id not in self.link_state_database.get(sender_id, {}):
                if sender_id not in self.link_state_database:
                    self.link_state_database[sender_id] = {}
                self.link_state_database[sender_id][neighbor_id] = cost
                updated = True
        return updated

    def rebroadcast_lsp(self, lsp, sender_addr):
        lsp_data = json.dumps(lsp).encode('utf-8')
        for neighbor_id, (_, port) in self.neighbors.items():
            if ('localhost', port) != sender_addr:
                #print(f"Router {self.router_id}: Rebroadcasting LSP to Neighbor {neighbor_id}")
                #print(lsp)
                self.socket.sendto(lsp_data, ('localhost', port))

    def check_neighbor_failures(self):
        failure_detected = False
        current_time = time.time()
        for neighbor_id, last_heartbeat in list(self.last_heartbeat_received.items()):
            if current_time - last_heartbeat > 3 * UPDATE_INTERVAL:
                # Neighbor is considered failed, remove from neighbors and link-state database
                self.neighbors.pop(neighbor_id, None)
                self.link_state_database.pop(neighbor_id, None)
                self.last_heartbeat_received.pop(neighbor_id, None)
                #print(f"Router {self.router_id}: Neighbor {neighbor_id} is considered failed.")
                failure_detected = True
        
        if failure_detected:
            # Broadcast new LSP to inform other routers of the topology change
            self.send_lsp_to_neighbors()


    def __str__(self):
        return f"Router ID: {self.router_id}, Port: {self.port}, Neighbors: {self.neighbors}"


    def initialize_routing_table(self):
        self.routing_table = {neighbor: (cost, neighbor) for neighbor, (cost, _) in self.neighbors.items()}
        self.routing_table[self.router_id] = (0, self.router_id)

    def run_dijkstras_algorithm(self):
        # Initialize all nodes with infinity distance and set the source node distance to 0
        unvisited = {node: float('infinity') for node in self.link_state_database}
        unvisited[self.router_id] = 0
        visited = {}  # To keep track of visited nodes
        path = {}  # To store the shortest path tree

        while unvisited:
            # Select the unvisited node with the smallest distance
            min_node = min(unvisited, key=unvisited.get)
            visited[min_node] = unvisited[min_node]

            # Update distances of adjacent nodes of the selected node
            if min_node in self.link_state_database:
                for neighbor, cost in self.link_state_database[min_node].items():
                    if neighbor not in visited:
                        new_cost = unvisited[min_node] + cost
                        # If the newly calculated distance is less than the current, update the distance
                        if new_cost < unvisited.get(neighbor, float('infinity')):
                            unvisited[neighbor] = new_cost
                            path[neighbor] = min_node
            # Remove min_node from unvisited set
            unvisited.pop(min_node)

        # Update the routing table with the shortest distance and path to each node
        for node, cost in visited.items():
            self.routing_table[node] = (cost, path.get(node, node))


    def print_least_cost_paths(self):
        print(f"I am Router {self.router_id}")
        for destination, (cost, next_hop) in self.routing_table.items():
            if destination != self.router_id:
                path = self.construct_path(destination)
                print(f"Least cost path to router {destination}:{path} and the cost: {round(cost * 10) / 10}")

    def construct_path(self, destination):
        path = [destination]
        while destination in self.routing_table and self.routing_table[destination][1] != self.router_id:
            destination = self.routing_table[destination][1]
            path.insert(0, destination)
        path.insert(0, self.router_id)
        return ''.join(path)

    def update_routing_table(self):
        self.run_dijkstras_algorithm()
        self.print_least_cost_paths()

    def broadcast_lsp_periodically(self, update_interval):
        while self.active:
            self.send_lsp_to_neighbors()
            self.check_neighbor_failures()
            time.sleep(update_interval)

    def listen_for_lsp_header(self):
        while self.active:
            self.listen_for_lsp()

    def execute_dijkstra_periodically(self, route_update_interval):
        while self.active:
            self.update_routing_table()
            time.sleep(route_update_interval)


def initialize_router_from_config(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        num_neighbors = int(lines[0].strip())
        router_id = file_path.replace('config', '').replace('.txt', '')
        neighbors = {}
        for i in range(1, num_neighbors + 1):
            parts = lines[i].strip().split(' ')
            neighbor_id = parts[0]
            cost = float(parts[1])
            port = int(parts[2])
            neighbors[neighbor_id] = (cost, port)
        router = Router(router_id, int(sys.argv[2]), neighbors)
        router.initialize_link_state_database()
        router.initialize_socket()  # Initialize the socket here
    return router

# Make calls to class:
UPDATE_INTERVAL = 1  # seconds, for LSP broadcast
ROUTE_UPDATE_INTERVAL = 30  # seconds, for running Dijkstra and printing routes

router = initialize_router_from_config(sys.argv[3])

threading.Thread(target=router.broadcast_lsp_periodically, args=(UPDATE_INTERVAL,)).start()
threading.Thread(target=router.listen_for_lsp_header, args=()).start()
threading.Thread(target=router.execute_dijkstra_periodically, args=(ROUTE_UPDATE_INTERVAL,)).start()
