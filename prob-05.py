# Model and resolve a simple fastest path problem using the Dijkstra algorithm
import heapq

def dijkstra(graph, start):
    queue = [(0, start)]
    distances = {node: float('inf') for node in graph}
    distances[start] = 0
    while queue:
        current_distance, current_node = heapq.heappop(queue)
        if current_distance > distances[current_node]:
            continue
        for neighbor, weight in graph[current_node].items():
            distance = current_distance + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                heapq.heappush(queue, (distance, neighbor))
    return distances
# Example usage:
if __name__ == "__main__":
    graph = {
        'A': {'B': 1, 'C': 4},
        'B': {'A': 1, 'C': 2, 'D': 5},
        'C': {'A': 4, 'B': 2, 'D': 1},
        'D': {'B': 5, 'C': 1}
    }
    start_node = 'A'
    shortest_paths = dijkstra(graph, start_node)
    print(f"Shortest paths from {start_node}: {shortest_paths}")
# Output should be:
# Shortest paths from A: {'A': 0, 'B': 1, 'C': 3, 'D': 4}
# This indicates the shortest distance from node 'A' to all other nodes in the graph.


