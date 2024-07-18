# Link-State-Routing-Protocol

### Introduction <br>
This project implements a Link-State Routing (LSR) protocol to demonstrate a distributed routing algorithm. Each router broadcasts its link-state information to the entire network and computes the least-cost paths using Dijkstra's algorithm. The protocol is designed to handle dynamic network conditions, including node failures and rejoining nodes.

### Features <br>
**Link-State Packets (LSPs):** Each router broadcasts its LSP containing its ID, neighbors, and link costs. <br>
**Sequence Numbers and Timestamps:** Prevent processing of outdated LSPs with included sequence numbers and timestamps. <br>
**Periodic Updates:** Routers periodically broadcast LSPs to ensure all nodes have up-to-date topology information. <br>
**Dijkstra's Algorithm:** Computes the least-cost paths from each router to all other nodes at regular intervals. <br>
**Failure Detection:** Uses heartbeats to detect node failures and update the topology accordingly. <br>
**Node Rejoining:** Handles scenarios where previously failed nodes rejoin the network. <br>
**Multithreading:** Utilizes multiple threads to handle sending, receiving, and processing LSPs concurrently. <br>

### Implementation Details <br>
**Router Initialization:** Reads the configuration file to get the router ID, port number, and neighbor information. Initializes the link-state database and sequence number. <br>
**Broadcasting LSPs:** Creates and sends LSPs to all neighbors. Periodically rebroadcasts LSPs to ensure network convergence. <br>
**Receiving LSPs:** Listens for incoming LSPs, updates the link-state database, and rebroadcasts received LSPs if they are new or have higher sequence numbers. <br>
**Running Dijkstra's Algorithm:** Computes the shortest paths from the router to all other nodes using the updated link-state database. Outputs the least-cost paths and associated costs. <br>
**Handling Node Failures:** Uses periodic heartbeats to detect when a neighbor node has failed. Updates the topology and recomputes the shortest paths excluding the failed nodes. <br>
**Node Rejoining:** Detects when a previously failed node reestablishes communication. Updates the topology and includes the rejoined node in the shortest path computation. <br>

### How to Run
Prepare Configuration Files: Create configuration files for each router specifying neighbors and link costs.
Start Routers: Open multiple terminal windows and start the routing program for each router using the command:

python3 Lsr_Version_C.py [Router ID] [Port Number] [Config File]

Example:

python3 Lsr_Version_C.py A 5000 configA.txt

Monitor Output: Each router will periodically output the least-cost paths to all other routers.

### Topics Covered <br>
-Network Protocol Design
-Shortest Path Algorithms (Dijkstra's Algorithm)
-UDP Socket Programming
-Concurrency and Multithreading
-Fault Tolerance and Failure Recovery

### Conclusion <br>
This project demonstrates the design and implementation of a robust network protocol, handling dynamic network conditions and applying advanced programming techniques. The implementation is thoroughly tested and showcases a comprehensive understanding of computer networks and distributed systems.

Feel free to explore the code and use it as a reference for understanding link-state routing protocols and their practical applications. If you have any questions or suggestions, please open an issue or submit a pull request.
