import heapq

# Manhattan Distance Heuristic
def manhattan(p, q):
    return abs(p[0] - q[0]) + abs(p[1] - q[1])

def best_first_search(grid, start, goal):
    rows, cols = len(grid), len(grid[0])
    pq = []  # priority queue: stores (heuristic, (x, y))
    heapq.heappush(pq, (manhattan(start, goal), start))
    
    visited = set()
    parent = {}  # for reconstructing path
    
    # possible moves: up, down, left, right
    moves = [(1,0), (-1,0), (0,1), (0,-1)]
    
    while pq:
        h, (x, y) = heapq.heappop(pq)
        
        if (x, y) in visited:
            continue
        
        visited.add((x, y))
        
        # Goal Found
        if (x, y) == goal:
            # reconstruct path
            path = []
            while (x, y) != start:
                path.append((x, y))
                x, y = parent[(x, y)]
            path.append(start)
            return path[::-1], visited
        
        # Explore neighbors
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            
            if 0 <= nx < rows and 0 <= ny < cols:
                if (nx, ny) not in visited:
                    parent[(nx, ny)] = (x, y)
                    heapq.heappush(pq, (manhattan((nx, ny), goal), (nx, ny)))
    
    return None, visited


# ---------------------------
# Example Usage
# ---------------------------
grid = [
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0]
]

start = (0, 0)
goal = (2, 3)

path, explored = best_first_search(grid, start, goal)

print("Best-First Search Path:", path)
print("Visited Nodes:", explored)
