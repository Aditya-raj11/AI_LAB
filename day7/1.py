from collections import deque
import heapq

# ---------------- Heuristic (Manhattan Distance) ----------------
def heuristic(pos, remaining_goals, exit_pos):
    if not remaining_goals:
        return abs(pos[0] - exit_pos[0]) + abs(pos[1] - exit_pos[1])
    return min(abs(pos[0] - g[0]) + abs(pos[1] - g[1]) for g in remaining_goals)

# ---------------- Combined Search Function ----------------
def multi_goal_navigation(grid, start, goals, exit_pos):
    """
    grid       : 2D grid
    start      : (x, y)
    goals      : {(x,y): cost}
    exit_pos   : (x, y)
    """

    R, C = len(grid), len(grid[0])
    moves = [(0,1), (1,0), (0,-1), (-1,0)]
    all_goals = set(goals.keys())

    # Check if weighted or unweighted
    weighted = any(cost > 0 for cost in goals.values())

    start_state = (start[0], start[1], frozenset())

    # ---------------- BFS (Unweighted) ----------------
    if not weighted:
        queue = deque([(start_state, [])])
        visited = set([start_state])

        while queue:
            (x, y, collected), path = queue.popleft()

            if (x, y) in goals:
                collected |= {(x, y)}

            if collected == all_goals and (x, y) == exit_pos:
                return path + [(x, y)], len(path)

            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if 0 <= nx < R and 0 <= ny < C and grid[nx][ny] != '#':
                    state = (nx, ny, collected)
                    if state not in visited:
                        visited.add(state)
                        queue.append((state, path + [(x, y)]))

    # ---------------- A* (Weighted) ----------------
    else:
        pq = []
        visited = {}

        heapq.heappush(pq, (0, 0, start_state, []))

        while pq:
            f, cost, (x, y, collected), path = heapq.heappop(pq)

            if (x, y) in goals and (x, y) not in collected:
                cost += goals[(x, y)]
                collected |= {(x, y)}

            if collected == all_goals and (x, y) == exit_pos:
                return path + [(x, y)], cost

            state = (x, y, collected)
            if state in visited and visited[state] <= cost:
                continue
            visited[state] = cost

            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if 0 <= nx < R and 0 <= ny < C and grid[nx][ny] != '#':
                    remaining = all_goals - collected
                    h = heuristic((nx, ny), remaining, exit_pos)
                    heapq.heappush(
                        pq,
                        (cost + 1 + h, cost + 1,
                         (nx, ny, collected), path + [(x, y)])
                    )

    return None

# ---------------- Driver Code ----------------
def main():
    grid = [
        ['S', '.', '.'],
        ['.', '#', 'G'],
        ['.', '.', 'E']
    ]

    start = (0, 0)
    exit_pos = (2, 2)

    print("---- BFS (Unweighted Goals) ----")
    goals_bfs = {(1, 2): 0}
    path, steps = multi_goal_navigation(grid, start, goals_bfs, exit_pos)
    print("Path:", path)
    print("Steps:", steps)

    print("\n---- A* (Weighted Goals) ----")
    goals_astar = {(1, 2): 5}
    path, cost = multi_goal_navigation(grid, start, goals_astar, exit_pos)
    print("Path:", path)
    print("Total Cost:", cost)

# ---------------- Run Program ----------------
if __name__ == "__main__":
    main()