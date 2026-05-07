import heapq
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Rectangle

class PathPlanner:
    def __init__(self, grid):
        self.grid = grid
        self.rows, self.cols = grid.shape

    def is_valid(self, r, c):
        return 0 <= r < self.rows and 0 <= c < self.cols and self.grid[r][c] == 0

    def get_neighbors(self, r, c, diagonal=False):
        moves = [(0,1),(1,0),(0,-1),(-1,0)]
        if diagonal:
            moves += [(1,1),(1,-1),(-1,1),(-1,-1)]

        for dr, dc in moves:
            nr, nc = r + dr, c + dc
            if self.is_valid(nr, nc):
                cost = 1.414 if dr != 0 and dc != 0 else 1
                yield (nr, nc), cost

    def bfs(self, start, goal):
        from collections import deque
        q = deque([start])
        came_from = {start: None}

        while q:
            cur = q.popleft()
            if cur == goal:
                return self.reconstruct(came_from, cur), len(came_from)

            for nb, _ in self.get_neighbors(*cur, diagonal=False):
                if nb not in came_from:
                    came_from[nb] = cur
                    q.append(nb)
        return None, len(came_from)

    def ucs(self, start, goal):
        pq = [(0, start)]
        came_from = {start: None}
        cost = {start: 0}

        while pq:
            g, cur = heapq.heappop(pq)
            if cur == goal:
                return self.reconstruct(came_from, cur), g, len(cost)

            for nb, c in self.get_neighbors(*cur, diagonal=False):
                nc = cost[cur] + c
                if nb not in cost or nc < cost[nb]:
                    cost[nb] = nc
                    heapq.heappush(pq, (nc, nb))
                    came_from[nb] = cur
        return None, 0, len(cost)

    def astar(self, start, goal):
        pq = [(0, start)]
        came_from = {start: None}
        cost = {start: 0}

        while pq:
            _, cur = heapq.heappop(pq)
            if cur == goal:
                return self.reconstruct(came_from, cur), cost[cur], len(cost)

            for nb, c in self.get_neighbors(*cur, diagonal=True):
                nc = cost[cur] + c
                if nb not in cost or nc < cost[nb]:
                    cost[nb] = nc
                    f = nc + np.hypot(nb[0]-goal[0], nb[1]-goal[1])
                    heapq.heappush(pq, (f, nb))
                    came_from[nb] = cur
        return None, 0, len(cost)

    def reconstruct(self, came_from, cur):
        path = [cur]
        while came_from[cur] is not None:
            cur = came_from[cur]
            path.append(cur)
        return path[::-1]


def animate(grid, path, title, color):
    rows, cols = grid.shape
    fig, ax = plt.subplots(figsize=(6, 6))

    ax.set_xlim(0, cols)
    ax.set_ylim(0, rows)
    ax.set_aspect("equal")
    ax.invert_yaxis()
    ax.set_title(title)

    for x in range(cols + 1):
        ax.axvline(x, color="lightgray", linewidth=0.8)
    for y in range(rows + 1):
        ax.axhline(y, color="lightgray", linewidth=0.8)

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 1:
                ax.add_patch(Rectangle((c, r), 1, 1, color="black"))

    py = [p[0] + 0.5 for p in path]
    px = [p[1] + 0.5 for p in path]

    ax.plot(px, py, color=color, linewidth=3, label="Path")
    ax.scatter(px[0], py[0], c="green", s=120, label="Start")
    ax.scatter(px[-1], py[-1], c="red", s=120, label="Goal")

    robot, = ax.plot(px[0], py[0], "o", color=color, markersize=10)

    def update(i):
        robot.set_data([px[i]], [py[i]])
        return robot,

    ani = FuncAnimation(fig, update, frames=len(px), interval=250, repeat=False)
    ax.legend()
    plt.show()
    return ani


if __name__ == "__main__":

    grid = np.array([
        [0,0,0,0,0,0,0,1,0,0],
        [0,1,1,1,0,1,0,1,0,0],
        [0,0,0,1,0,1,0,0,0,0],
        [0,1,0,0,0,1,1,1,1,0],
        [0,1,1,1,0,0,0,0,1,0],
        [0,0,0,1,1,1,0,1,1,0],
        [0,1,0,0,0,0,0,0,1,0],
        [0,1,0,1,1,1,0,1,1,0],
        [0,0,0,0,0,0,0,1,1,0],
        [0,0,0,0,0,0,0,0,1,0]
    ])

    start, goal = (0, 0), (9, 9)
    planner = PathPlanner(grid)

    bfs_path, bfs_nodes = planner.bfs(start, goal)
    print(f"BFS → Path Length: {len(bfs_path)} | Nodes Explored: {bfs_nodes}")
    animate(grid, bfs_path, "BFS Path", "blue")

    ucs_path, ucs_cost, ucs_nodes = planner.ucs(start, goal)
    print(f"UCS → Cost: {ucs_cost} | Path Length: {len(ucs_path)} | Nodes Explored: {ucs_nodes}")
    animate(grid, ucs_path, "UCS Path", "purple")

    astar_path, astar_cost, astar_nodes = planner.astar(start, goal)
    print(f"A* → Cost: {astar_cost:.2f} | Path Length: {len(astar_path)} | Nodes Explored: {astar_nodes}")
    animate(grid, astar_path, "A* Path", "orange")
