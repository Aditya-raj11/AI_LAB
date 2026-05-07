import heapq
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque

class SnakeAndLadderAI:
    def __init__(self, snakes, ladders, board_size=100):
        self.snakes = snakes
        self.ladders = ladders
        self.board_size = board_size
        self.jumps = {**snakes, **ladders}

    def get_neighbors(self, state):
        neighbors = []
        for dice in range(1, 7):
            nxt = state + dice
            if nxt <= self.board_size:
                if nxt in self.jumps:
                    nxt = self.jumps[nxt]
                neighbors.append(nxt)
        return neighbors

    def bfs(self):
        q = deque([(1, [1])])
        visited = {1}
        explored = 0

        while q:
            cur, path = q.popleft()
            explored += 1
            if cur == self.board_size:
                return path, explored
            for nb in self.get_neighbors(cur):
                if nb not in visited:
                    visited.add(nb)
                    q.append((nb, path + [nb]))
        return None, explored

    def dfs(self):
        stack = [(1, [1])]
        visited = set()
        explored = 0

        while stack:
            cur, path = stack.pop()
            explored += 1
            if cur == self.board_size:
                return path, explored
            if cur in visited:
                continue
            visited.add(cur)
            for nb in self.get_neighbors(cur):
                if nb not in visited:
                    stack.append((nb, path + [nb]))
        return None, explored

    def heuristic(self, state):
        return (self.board_size - state + 5) // 6

    def astar(self):
        pq = [(self.heuristic(1), 1, [1])]
        cost = {1: 0}
        explored = 0

        while pq:
            _, cur, path = heapq.heappop(pq)
            explored += 1
            if cur == self.board_size:
                return path, explored

            for nb in self.get_neighbors(cur):
                nc = cost[cur] + 1
                if nb not in cost or nc < cost[nb]:
                    cost[nb] = nc
                    heapq.heappush(
                        pq, (nc + self.heuristic(nb), nb, path + [nb])
                    )
        return None, explored


def draw_board(ax, snakes, ladders):
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.set_aspect("equal")
    ax.axis("off")

    for i in range(11):
        ax.plot([0, 10], [i, i], color="gray", lw=0.8)
        ax.plot([i, i], [0, 10], color="gray", lw=0.8)

    num = 1
    for r in range(10):
        row = range(10) if r % 2 == 0 else range(9, -1, -1)
        for c in row:
            ax.text(c + 0.5, 9.5 - r, str(num),
                    ha="center", va="center", fontsize=7)
            num += 1

    for s, e in ladders.items():
        x1, y1 = (s-1) % 10 + 0.5, 9 - (s-1)//10 + 0.5
        x2, y2 = (e-1) % 10 + 0.5, 9 - (e-1)//10 + 0.5
        ax.plot([x1, x2], [y1, y2], color="green", lw=3)

    for s, e in snakes.items():
        x1, y1 = (s-1) % 10 + 0.5, 9 - (s-1)//10 + 0.5
        x2, y2 = (e-1) % 10 + 0.5, 9 - (e-1)//10 + 0.5
        ax.plot([x1, x2], [y1, y2], color="red", lw=3)


def animate_path(path, title, snakes, ladders):
    fig, ax = plt.subplots(figsize=(6, 6))
    draw_board(ax, snakes, ladders)
    ax.set_title(title)

    coords = [((p-1) % 10 + 0.5, 9 - (p-1)//10 + 0.5) for p in path]
    token, = ax.plot(coords[0][0], coords[0][1], "bo", markersize=10)

    def update(i):
        token.set_data([coords[i][0]], [coords[i][1]])
        return token,

    ani = FuncAnimation(fig, update, frames=len(coords), interval=400, repeat=False)
    plt.show()
    return ani


if __name__ == "__main__":

    snakes = {16: 6, 47: 26, 49: 11, 56: 53, 62: 19,
              64: 60, 87: 24, 93: 73, 95: 75, 98: 78}

    ladders = {1: 38, 4: 14, 9: 31, 21: 42, 28: 84,
               36: 44, 51: 67, 71: 91, 80: 100}

    ai = SnakeAndLadderAI(snakes, ladders)

    print("\n--- Assignment 7: Snake & Ladder AI Comparison ---\n")

    bfs_path, bfs_nodes = ai.bfs()
    print(f"BFS → Moves: {len(bfs_path)-1}, Nodes Explored: {bfs_nodes}")
    animate_path(bfs_path, "BFS Solution", snakes, ladders)

    dfs_path, dfs_nodes = ai.dfs()
    print(f"DFS → Moves: {len(dfs_path)-1}, Nodes Explored: {dfs_nodes}")
    animate_path(dfs_path, "DFS Solution", snakes, ladders)

    astar_path, astar_nodes = ai.astar()
    print(f"A* → Moves: {len(astar_path)-1}, Nodes Explored: {astar_nodes}")
    animate_path(astar_path, "A* Solution", snakes, ladders)
