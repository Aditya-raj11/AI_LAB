# Assignment 10: Comparative Study of Search Algorithms
# Domain: Grid Pathfinding
# Algorithms: BFS, DFS, Bi-directional BFS, UCS, Best-First Search, A*

import time
import heapq
from collections import deque
import matplotlib.pyplot as plt
import numpy as np

# ── Grid Setup ──────────────────────────────────
# 0 = free, 1 = wall
GRID = [
    [0,0,1,0,0,0,0,0,0,0],
    [0,0,1,0,1,1,1,0,1,0],
    [0,0,0,0,1,0,0,0,1,0],
    [0,1,1,0,1,0,1,1,1,0],
    [0,0,0,0,0,0,0,0,0,0],
    [1,1,0,1,1,0,1,1,0,0],
    [0,0,0,0,1,0,0,0,0,0],
    [0,1,1,0,0,0,1,1,1,0],
    [0,0,1,0,1,0,0,0,0,0],
    [0,0,0,0,1,0,1,0,0,0],
]

START = (0, 0)
GOAL  = (9, 9)
ROWS  = len(GRID)
COLS  = len(GRID[0])


def neighbors(r, c):
    for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
        nr, nc = r+dr, c+dc
        if 0 <= nr < ROWS and 0 <= nc < COLS and GRID[nr][nc] == 0:
            yield (nr, nc)


def reconstruct(parent, node):
    path = []
    while node:
        path.append(node)
        node = parent[node]
    return path[::-1]


# ── BFS ─────────────────────────────────────────
def bfs():
    queue   = deque([(START, [START])])
    visited = {START}
    count   = 0
    while queue:
        node, path = queue.popleft()
        count += 1
        if node == GOAL:
            return path, count
        for nb in neighbors(*node):
            if nb not in visited:
                visited.add(nb)
                queue.append((nb, path + [nb]))
    return [], count


# ── DFS ─────────────────────────────────────────
def dfs():
    stack   = [(START, [START])]
    visited = {START}
    count   = 0
    while stack:
        node, path = stack.pop()
        count += 1
        if node == GOAL:
            return path, count
        for nb in neighbors(*node):
            if nb not in visited:
                visited.add(nb)
                stack.append((nb, path + [nb]))
    return [], count


# ── Bidirectional BFS ────────────────────────────
def bidirectional_bfs():
    fq, bq   = deque([START]), deque([GOAL])
    fv, bv   = {START: None}, {GOAL: None}
    count    = 0

    def build(meet):
        p = []
        n = meet
        while n: p.append(n); n = fv[n]
        p.reverse()
        n = bv[meet]
        while n: p.append(n); n = bv[n]
        return p

    while fq or bq:
        if fq:
            n = fq.popleft(); count += 1
            for nb in neighbors(*n):
                if nb not in fv:
                    fv[nb] = n; fq.append(nb)
                if nb in bv:
                    return build(nb), count
        if bq:
            n = bq.popleft(); count += 1
            for nb in neighbors(*n):
                if nb not in bv:
                    bv[nb] = n; bq.append(nb)
                if nb in fv:
                    return build(nb), count
    return [], count


# ── UCS ─────────────────────────────────────────
def ucs():
    heap    = [(0, START, [START])]
    visited = {}
    count   = 0
    while heap:
        cost, node, path = heapq.heappop(heap)
        if node in visited: continue
        visited[node] = cost; count += 1
        if node == GOAL:
            return path, count
        for nb in neighbors(*node):
            if nb not in visited:
                heapq.heappush(heap, (cost+1, nb, path+[nb]))
    return [], count


# ── Best-First Search ────────────────────────────
def heuristic(a, b=GOAL):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def best_first():
    heap    = [(heuristic(START), START, [START])]
    visited = {START}
    count   = 0
    while heap:
        _, node, path = heapq.heappop(heap)
        count += 1
        if node == GOAL:
            return path, count
        for nb in neighbors(*node):
            if nb not in visited:
                visited.add(nb)
                heapq.heappush(heap, (heuristic(nb), nb, path+[nb]))
    return [], count


# ── A* ──────────────────────────────────────────
def astar():
    heap   = [(heuristic(START), 0, START, [START])]
    g_cost = {START: 0}
    count  = 0
    while heap:
        f, g, node, path = heapq.heappop(heap)
        if g > g_cost.get(node, float('inf')): continue
        count += 1
        if node == GOAL:
            return path, count
        for nb in neighbors(*node):
            ng = g + 1
            if ng < g_cost.get(nb, float('inf')):
                g_cost[nb] = ng
                heapq.heappush(heap, (ng+heuristic(nb), ng, nb, path+[nb]))
    return [], count


# ── Run & Measure ────────────────────────────────
ALGOS = {
    "BFS":          bfs,
    "DFS":          dfs,
    "Bi-BFS":       bidirectional_bfs,
    "UCS":          ucs,
    "Best-First":   best_first,
    "A*":           astar,
}
OPTIMAL = {"BFS": True, "DFS": False, "Bi-BFS": True,
           "UCS": True, "Best-First": False, "A*": True}

results = {}
for name, fn in ALGOS.items():
    t0 = time.perf_counter()
    path, nodes = fn()
    elapsed = (time.perf_counter() - t0) * 1000
    results[name] = {"path": path, "nodes": nodes,
                     "time": elapsed, "len": len(path)}

# ── Print Table ──────────────────────────────────
print(f"\n{'Algorithm':<14} {'Nodes':>7} {'Time(ms)':>10} {'Path Len':>9} {'Optimal':>8}")
print("-" * 52)
for name, r in results.items():
    print(f"{name:<14} {r['nodes']:>7} {r['time']:>10.4f} "
          f"{r['len']:>9} {'Yes' if OPTIMAL[name] else 'No':>8}")

# ── Visualisation 1: Grid Paths ──────────────────
COLORS = ["#e74c3c","#3498db","#2ecc71","#f39c12","#9b59b6","#1abc9c"]
fig, axes = plt.subplots(2, 3, figsize=(13, 8))
fig.suptitle("Assignment 10 — Search Algorithm Grid Paths", fontsize=13, fontweight='bold')

for ax, (name, r), color in zip(axes.flat, results.items(), COLORS):
    img = np.ones((ROWS, COLS, 3))
    for i in range(ROWS):
        for j in range(COLS):
            if GRID[i][j] == 1:
                img[i,j] = [0.2, 0.2, 0.2]
    rgb = [int(color[k:k+2],16)/255 for k in (1,3,5)]
    for (pr, pc) in r["path"]:
        img[pr, pc] = rgb
    img[START[0], START[1]] = [0, 0.8, 0]
    img[GOAL[0],  GOAL[1]]  = [0.9, 0.1, 0.1]
    ax.imshow(img, interpolation='nearest')
    ax.set_title(f"{name}  |  Nodes: {r['nodes']}  |  Optimal: {'✓' if OPTIMAL[name] else '✗'}",
                 fontsize=9)
    ax.axis('off')

plt.tight_layout()
plt.savefig("algo_grid_paths.png", dpi=150, bbox_inches='tight')
plt.show()

# ── Visualisation 2: Comparison Bar Charts ───────
names  = list(results.keys())
nodes  = [results[n]["nodes"] for n in names]
times  = [results[n]["time"]  for n in names]
lengths= [results[n]["len"]   for n in names]
x = range(len(names))

fig, axes = plt.subplots(1, 3, figsize=(14, 4))
fig.suptitle("Assignment 10 — Algorithm Comparison", fontsize=13, fontweight='bold')

for ax, vals, title, ylabel in zip(
    axes,
    [nodes, times, lengths],
    ["Nodes Explored", "Time Taken (ms)", "Path Length"],
    ["Count", "ms", "Steps"]
):
    bars = ax.bar(x, vals, color=COLORS, edgecolor='white')
    for b, v in zip(bars, vals):
        ax.text(b.get_x()+b.get_width()/2, b.get_height(), f"{v:.2f}",
                ha='center', va='bottom', fontsize=8)
    ax.set_xticks(list(x)); ax.set_xticklabels(names, rotation=20, ha='right')
    ax.set_title(title); ax.set_ylabel(ylabel)
    ax.grid(axis='y', alpha=0.3); ax.spines[['top','right']].set_visible(False)

plt.tight_layout()
plt.savefig("algo_comparison_bars.png", dpi=150, bbox_inches='tight')
plt.show()
