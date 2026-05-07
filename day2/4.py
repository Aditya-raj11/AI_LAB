import heapq

def uniform_cost_search(graph, start, goal):
    pq = []  # priority queue: stores (cost, node, path)
    heapq.heappush(pq, (0, start, [start]))
    
    visited = set()
    
    while pq:
        cost, node, path = heapq.heappop(pq)
        
        if node in visited:
            continue
        
        visited.add(node)
        
        # Goal found
        if node == goal:
            return cost, path
        
        # Expand neighbors
        for neighbor, edge_cost in graph[node]:
            if neighbor not in visited:
                heapq.heappush(pq, (cost + edge_cost, neighbor, path + [neighbor]))
    
    return float("inf"), []  # goal not reachable


# ---------------------------
# Example Usage
# ---------------------------

graph = {
    'A': [('B', 2), ('C', 5)],
    'B': [('D', 4), ('E', 1)],
    'C': [('E', 2)],
    'D': [('F', 3)],
    'E': [('F', 1)],
    'F': []
}

start = 'A'
goal = 'F'

cost, path = uniform_cost_search(graph, start, goal)

print("Optimal cost:", cost)
print("Optimal path:", path)
