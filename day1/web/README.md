# 🔍 AI Lab — Day 1: Search Algorithm Visualizers

An interactive web application that lets you **see** how fundamental search algorithms work, step by step. Built with Next.js and deployable on Vercel.

> **Live Demo:** _[Add your Vercel URL here after deploying]_

---

## 📚 Table of Contents

1. [What This Project Covers](#what-this-project-covers)
2. [Theoretical Background](#theoretical-background)
   - [What Is a Search Algorithm?](#what-is-a-search-algorithm)
   - [Breadth-First Search (BFS)](#1-breadth-first-search-bfs)
   - [Depth-First Search (DFS)](#2-depth-first-search-dfs)
   - [BFS vs DFS — Comparison Table](#bfs-vs-dfs--comparison-table)
   - [Bidirectional Search](#3-bidirectional-search)
   - [Recursive Backtracking (Maze Generation)](#4-recursive-backtracking-maze-generation)
3. [How the Visualizers Work](#how-the-visualizers-work)
4. [Project Structure](#project-structure)
5. [How to Run Locally](#how-to-run-locally)
6. [How to Deploy to Vercel](#how-to-deploy-to-vercel)
7. [How to Add Future Days](#how-to-add-future-days)
8. [Controls Reference](#controls-reference)
9. [Key Concepts Glossary](#key-concepts-glossary)
10. [References](#references)

---

## What This Project Covers

This project implements and visualizes **four core algorithms** that are fundamental to Artificial Intelligence and Computer Science:

| Algorithm | Category | Used In |
|-----------|----------|---------|
| **BFS** (Breadth-First Search) | Uninformed Search | Maze Solver |
| **DFS** (Depth-First Search) | Uninformed Search | Maze Solver |
| **Bidirectional Search** | Uninformed Search | Route Finder |
| **Recursive Backtracking** | Constraint Satisfaction / Maze Generation | Maze Generator |

---

## Theoretical Background

### What Is a Search Algorithm?

A **search algorithm** is a procedure that systematically explores a space of possible states to find a path from an **initial state** (start) to a **goal state** (end). In AI, this is one of the most foundational concepts because many real-world problems can be modeled as search problems:

- Finding a route on a map (GPS navigation)
- Solving a puzzle (Rubik's cube, Sudoku)
- Game playing (Chess, Go)
- Robot motion planning

Every search algorithm works with these core concepts:

| Term | Meaning |
|------|---------|
| **State** | A specific configuration of the problem (e.g., a cell in the maze) |
| **State Space** | The set of ALL possible states |
| **Initial State** | Where we start (e.g., top-left corner of the maze) |
| **Goal State** | Where we want to reach (e.g., bottom-right corner) |
| **Successor Function** | Given a state, what states can we move to next? (e.g., neighboring cells) |
| **Frontier** | States we have discovered but not yet explored |
| **Visited Set** | States we have already explored (to avoid loops) |
| **Path** | The sequence of states from start to goal |

---

### 1. Breadth-First Search (BFS)

#### The Idea

BFS explores the search space **level by level**. It first visits all nodes at distance 1 from the start, then all nodes at distance 2, then distance 3, and so on. It uses a **queue** (First-In, First-Out) to decide which node to explore next.

Think of it like dropping a stone in a pond — the ripples expand outward equally in all directions.

#### Algorithm (Step by Step)

```
1. Create a queue Q and enqueue the start node.
2. Create a set VISITED (initially empty).
3. While Q is not empty:
   a. Dequeue the FIRST element from Q. Call it CURRENT.
   b. If CURRENT is the goal → return the path. Done!
   c. Mark CURRENT as visited.
   d. For each unvisited neighbor of CURRENT:
      - Mark it as discovered (so we don't add it again).
      - Enqueue it into Q along with the path taken to reach it.
4. If Q is empty and goal was never found → No path exists.
```

#### Why BFS Uses a Queue

A queue processes elements in **FIFO** (First-In, First-Out) order. This means nodes discovered first are explored first. Since nodes at distance 1 are discovered before nodes at distance 2, BFS naturally explores in expanding "layers."

#### JavaScript Implementation (from this project)

```javascript
// BFS uses shift() to dequeue from the front (FIFO behavior)
const [node, path] = frontier.shift();
```

#### Properties of BFS

| Property | Value |
|----------|-------|
| **Complete?** | ✅ Yes — if a solution exists, BFS will find it |
| **Optimal?** | ✅ Yes — BFS always finds the **shortest path** (in terms of number of edges) |
| **Time Complexity** | O(b^d) where b = branching factor, d = depth of solution |
| **Space Complexity** | O(b^d) — BFS must store all nodes at the current level |

#### When to Use BFS

- When you need the **shortest path** (minimum number of steps).
- When the search tree is not very deep.
- When all edges have equal cost (unweighted graph).

#### When NOT to Use BFS

- When the search space is very large (BFS uses a lot of memory).
- When edges have different costs (use Dijkstra's or A* instead).

---

### 2. Depth-First Search (DFS)

#### The Idea

DFS explores the search space by going **as deep as possible** along one branch before backtracking. It uses a **stack** (Last-In, First-Out) to decide which node to explore next.

Think of it like navigating a maze by always taking the first available turn, and only going back when you hit a dead end.

#### Algorithm (Step by Step)

```
1. Create a stack S and push the start node.
2. Create a set VISITED (initially empty).
3. While S is not empty:
   a. Pop the LAST element from S. Call it CURRENT.
   b. If CURRENT is the goal → return the path. Done!
   c. Mark CURRENT as visited.
   d. For each unvisited neighbor of CURRENT:
      - Mark it as discovered.
      - Push it onto S along with the path taken to reach it.
4. If S is empty and goal was never found → No path exists.
```

#### Why DFS Uses a Stack

A stack processes elements in **LIFO** (Last-In, First-Out) order. This means the most recently discovered node is explored first. This causes DFS to "dive" deep into one branch before considering alternatives.

#### JavaScript Implementation (from this project)

```javascript
// DFS uses pop() to take from the end (LIFO behavior)
const [node, path] = frontier.pop();
```

#### The Elegant Difference

Notice that the **only difference** between BFS and DFS in our code is:
- BFS: `frontier.shift()` (take from front = queue)
- DFS: `frontier.pop()` (take from back = stack)

Everything else is identical! This is why they share the same `searchTrace()` function in the codebase.

#### Properties of DFS

| Property | Value |
|----------|-------|
| **Complete?** | ⚠️ Only if the graph is finite and we track visited nodes |
| **Optimal?** | ❌ No — DFS does NOT guarantee the shortest path |
| **Time Complexity** | O(b^m) where b = branching factor, m = maximum depth |
| **Space Complexity** | O(b × m) — DFS only stores nodes along the current path |

#### When to Use DFS

- When memory is limited (DFS uses much less memory than BFS).
- When you need to check if a path **exists** (not necessarily the shortest).
- For topological sorting, cycle detection, and connected component analysis.

#### When NOT to Use DFS

- When you need the shortest path.
- When the search space has infinite or very deep branches (DFS may never terminate).

---

### BFS vs DFS — Comparison Table

| Aspect | BFS | DFS |
|--------|-----|-----|
| **Data Structure** | Queue (FIFO) | Stack (LIFO) |
| **Exploration Pattern** | Level by level (wide) | Branch by branch (deep) |
| **Shortest Path?** | ✅ Always | ❌ Not guaranteed |
| **Memory Usage** | 🔴 High (stores entire level) | 🟢 Low (stores current path) |
| **Complete?** | ✅ Yes | ⚠️ Only with visited tracking |
| **Best For** | Shortest path problems | Existence checks, puzzles |

#### Visual Intuition

```
        S (Start)
       / \
      A   B
     / \   \
    C   D   E
   /       / \
  F       G   Goal

BFS order: S → A → B → C → D → E → F → G → Goal
  (explores level by level: depth 0, then 1, then 2, then 3)

DFS order: S → A → C → F → D → B → E → G → Goal
  (dives deep into left branch first, then backtracks)
```

---

### 3. Bidirectional Search

#### The Idea

Instead of searching from just the start node, Bidirectional Search runs **two BFS searches simultaneously**:
- One **forward** from the start node.
- One **backward** from the goal node.

The search terminates when the two frontiers **meet** — i.e., when a node explored by the forward search is also discovered by the backward search (or vice versa).

#### Why Is This Faster?

Imagine a search tree where each node has `b` children (branching factor = b) and the solution is at depth `d`. 

- **Regular BFS** explores O(b^d) nodes.
- **Bidirectional Search** explores O(2 × b^(d/2)) = O(b^(d/2)) nodes.

For b = 10 and d = 6:
- BFS: 10^6 = **1,000,000 nodes**
- Bidirectional: 2 × 10^3 = **2,000 nodes**

That's a **500x reduction** in the number of nodes explored!

#### Algorithm (Step by Step)

```
1. Create two queues: FRONT_Q (start node) and BACK_Q (goal node).
2. Create two visited sets: FRONT_VISITED and BACK_VISITED.
3. Create two parent maps: FRONT_PARENT and BACK_PARENT.
4. While both queues are non-empty:
   a. FORWARD STEP:
      - Dequeue from FRONT_Q. Call it NODE.
      - For each unvisited neighbor of NODE:
        - Add to FRONT_VISITED and FRONT_Q.
        - Record parent: FRONT_PARENT[neighbor] = NODE.
        - If neighbor is in BACK_VISITED → MEETING POINT FOUND!
   b. BACKWARD STEP:
      - Dequeue from BACK_Q. Call it NODE.
      - For each unvisited neighbor of NODE:
        - Add to BACK_VISITED and BACK_Q.
        - Record parent: BACK_PARENT[neighbor] = NODE.
        - If neighbor is in FRONT_VISITED → MEETING POINT FOUND!
5. When meeting point M is found:
   - Build path from START to M using FRONT_PARENT.
   - Build path from M to GOAL using BACK_PARENT.
   - Concatenate both paths → Final route!
```

#### Path Reconstruction

```
FRONT_PARENT: {A: null, B: A, C: B, M: C}
BACK_PARENT:  {G: null, F: G, E: F, M: E}

Path from START to M:  M → C → B → A → START  (reversed: START → A → B → C → M)
Path from M to GOAL:   M → E → F → G → GOAL

Full path: START → A → B → C → M → E → F → G → GOAL
```

#### Properties of Bidirectional Search

| Property | Value |
|----------|-------|
| **Complete?** | ✅ Yes |
| **Optimal?** | ✅ Yes (when both sides use BFS) |
| **Time Complexity** | O(b^(d/2)) — exponentially better than BFS |
| **Space Complexity** | O(b^(d/2)) |

#### When to Use Bidirectional Search

- When you know both the start and goal states in advance.
- When the graph is very large.
- When you need optimal paths but BFS is too slow.

#### When NOT to Use

- When the goal state is unknown (e.g., "find any solution").
- When the graph is directed and edges cannot be traversed backward.

---

### 4. Recursive Backtracking (Maze Generation)

#### The Idea

Recursive Backtracking is a technique for generating **perfect mazes** (mazes with exactly one solution and no loops). It is based on DFS:

1. Start with a grid where every cell is a **wall**.
2. Pick a starting cell and mark it as a **passage**.
3. Randomly choose an unvisited neighboring cell (2 cells away).
4. Remove the wall between the current cell and the chosen cell.
5. Recursively repeat from the chosen cell.
6. When no unvisited neighbors exist, **backtrack** to the previous cell.

#### Why It's Called "Backtracking"

The term **backtracking** refers to the fundamental problem-solving strategy of:
1. Making a choice.
2. Exploring that choice fully.
3. If the choice leads to a dead end, **undoing** it (going back) and trying a different choice.

In maze generation, "backtracking" happens when the algorithm reaches a cell that has no unvisited neighbors — it returns to the previous cell and tries a different direction.

#### Algorithm (Step by Step)

```
1. Initialize grid: ALL cells are walls (value = 1).
2. Define function CARVE(row, col):
   a. Set grid[row][col] = 0 (make it a passage).
   b. Get list of directions: [(0,2), (0,-2), (2,0), (-2,0)].
   c. Shuffle the directions randomly.
   d. For each direction (dr, dc):
      - Compute neighbor: (row + dr, col + dc).
      - If neighbor is within bounds AND is still a wall:
        - Remove the wall between: grid[row + dr/2][col + dc/2] = 0.
        - Recursively call CARVE(row + dr, col + dc).
3. Call CARVE(0, 0) to start.
```

#### Why Step by 2?

The maze grid alternates between **cells** and **walls**:

```
Cell  Wall  Cell  Wall  Cell
Wall  Wall  Wall  Wall  Wall
Cell  Wall  Cell  Wall  Cell
Wall  Wall  Wall  Wall  Wall
Cell  Wall  Cell  Wall  Cell
```

When we move by 2, we jump from cell to cell. The cell at the midpoint (step by 1) is the wall we "carve" to create a passage.

#### Why This Creates a "Perfect" Maze

Because we use DFS (recursion), and we never revisit cells, the carved passages form a **spanning tree** of the grid graph. A spanning tree has exactly one path between any two nodes, which is exactly what a perfect maze is.

#### JavaScript Implementation (from this project)

```javascript
function generateTreeMaze(rows, cols) {
  // Start with all walls
  const maze = Array.from({length: rows}, () => Array(cols).fill(1));

  function carve(r, c) {
    maze[r][c] = 0;  // Mark as passage
    // Randomize directions
    const dirs = [[0,2],[0,-2],[2,0],[-2,0]];
    for (let i = dirs.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [dirs[i], dirs[j]] = [dirs[j], dirs[i]];  // Fisher-Yates shuffle
    }
    for (const [dr, dc] of dirs) {
      const nr = r + dr, nc = c + dc;
      if (nr >= 0 && nr < rows && nc >= 0 && nc < cols && maze[nr][nc] === 1) {
        maze[r + dr/2][c + dc/2] = 0;  // Carve the wall between
        carve(nr, nc);                   // Recurse
      }
    }
  }

  carve(0, 0);
  return maze;
}
```

#### Properties

| Property | Value |
|----------|-------|
| **Time Complexity** | O(rows × cols) — visits each cell once |
| **Space Complexity** | O(rows × cols) — recursion stack in worst case |
| **Maze Type** | Perfect (exactly one solution, no loops) |
| **Bias** | Long, winding corridors (DFS characteristic) |

---

## How the Visualizers Work

### Maze Solver

1. The maze is represented as a 2D grid where `0` = open path and `1` = wall.
2. When you click "Run Search", the app creates a **generator function** that yields each step of the algorithm.
3. A timer (`setTimeout`) reads one step at a time and updates the grid's colors, creating the animation.
4. Each cell is colored based on its state:
   - **Blue** = Start node
   - **Red** = Goal node
   - **Dark** = Wall
   - **Teal** = Visited
   - **Blue-gray** = In the frontier (discovered but not yet explored)
   - **Yellow** = Currently being explored
   - **Green** = Part of the final solution path

### Route Finder

1. The graph is represented as an **adjacency list** (`{ "A": ["B", "C"], "B": ["A", "D"] ... }`).
2. Nodes are drawn on an HTML5 Canvas with their positions stored as `{ "A": [x, y] }`.
3. The Bidirectional Search runs as a generator, yielding forward and backward expansion steps alternately.
4. Node colors indicate which search wave has reached them:
   - **Blue** = Forward search visited
   - **Pink** = Backward search visited
   - **Purple** = Both searches have reached this node
   - **Green** = Meeting point
   - **Gold** = Final route

---

## Project Structure

```
day1/web/
├── app/
│   ├── globals.css              # Design system tokens, animations
│   ├── layout.js                # Root HTML layout, SEO meta tags
│   ├── page.js                  # Dashboard — expandable day card grid
│   ├── page.module.css          # Dashboard styles
│   └── day1/
│       ├── page.js              # Day 1 hub — links to tools
│       ├── day1.module.css
│       ├── maze/
│       │   ├── page.js          # Maze Solver (BFS + DFS + Backtracking)
│       │   └── maze.module.css
│       └── route/
│           ├── page.js          # Route Finder (Bidirectional Search)
│           └── route.module.css
├── package.json
└── README.md                    # ← You are here
```

---

## How to Run Locally

**Prerequisites:** Node.js 18+ installed.

```bash
cd day1/web
npm install
npm run dev
```

Open **http://localhost:3000** in your browser.

---

## How to Deploy to Vercel

1. Push the `day1/web` folder to a GitHub repository.
2. Go to [vercel.com](https://vercel.com) and sign in with GitHub.
3. Click **"New Project"** → Import your repository.
4. Set **Root Directory** to `day1/web`.
5. Click **Deploy**. You will receive a live URL in about 60 seconds.

---

## How to Add Future Days

This project is designed to be **expandable**. To add Day 2:

1. In `app/page.js`, add a new entry to the `days` array:

```javascript
{
  day: 2,
  title: "Heuristic Search",
  desc: "A*, UCS, and Best-First Search on grid environments.",
  topics: ["A*", "UCS", "Best-First", "Manhattan Distance"],
  icon: "🧭",
  gradient: "linear-gradient(135deg, #22c55e, #06b6d4)",
  iconBg: "rgba(34, 197, 94, 0.15)",
  href: "/day2",
},
```

2. Create `app/day2/page.js` with your new visualizer content.
3. The dashboard will automatically show the new card.

---

## Controls Reference

### Maze Solver

| Control | Action |
|---------|--------|
| **Click a cell** | Toggle wall on/off |
| **BFS / DFS toggle** | Switch the search algorithm |
| **Speed slider** | Control animation speed (fast ↔ slow) |
| **▶ Run Search** | Start the algorithm visualization |
| **🌲 Generate Tree Maze** | Create a random perfect maze via backtracking |
| **↺ Sample Maze** | Reload the default 5×5 maze |
| **✕ Clear Maze** | Remove all walls |

### Route Finder

| Control | Action |
|---------|--------|
| **Left-click + drag a node** | Move the node |
| **Double-click empty space** | Add a new node |
| **Double-click a node** | Delete the node and its connections |
| **Right-click + drag between two nodes** | Connect them (or disconnect if already connected) |
| **Start / Goal dropdowns** | Select which nodes to search between |
| **▶ Run Search** | Start the Bidirectional Search animation |
| **Sample** | Reload the default A–F graph |
| **Random** | Generate a random graph |
| **Clear** | Remove all nodes and edges |

---

## Key Concepts Glossary

| Term | Definition |
|------|------------|
| **Graph** | A set of nodes (vertices) connected by edges. Can be directed or undirected. |
| **Adjacency List** | A way to represent a graph where each node stores a list of its neighbors. Used in this project. |
| **Tree** | A connected graph with no cycles. Every maze generated by backtracking is a tree. |
| **Spanning Tree** | A tree that includes every node of the original graph. A perfect maze IS a spanning tree of the grid. |
| **Queue (FIFO)** | First-In, First-Out data structure. Used by BFS. |
| **Stack (LIFO)** | Last-In, First-Out data structure. Used by DFS. |
| **Frontier** | The set of nodes discovered but not yet fully explored. |
| **Visited Set** | Nodes that have been fully explored. Prevents infinite loops. |
| **Branching Factor (b)** | Average number of children per node. In a grid maze, b ≤ 4 (up, down, left, right). |
| **Depth (d)** | The length of the shortest path from start to goal. |
| **Complete Algorithm** | An algorithm that is guaranteed to find a solution if one exists. |
| **Optimal Algorithm** | An algorithm that is guaranteed to find the best (shortest/cheapest) solution. |
| **Backtracking** | A problem-solving strategy: try a choice, and if it fails, undo it and try the next option. |
| **Generator Function** | A JavaScript function that can pause (`yield`) and resume, producing values one at a time. Used here to animate algorithms step-by-step. |
| **Perfect Maze** | A maze with exactly one path between any two cells (no loops, no isolated areas). |
| **Fisher-Yates Shuffle** | An algorithm for randomly shuffling an array in O(n) time. Used to randomize maze directions. |
| **Heuristic** | An estimate of the cost to reach the goal. Not used in Day 1 (these are uninformed searches), but essential for A* in later days. |

---

## References

1. **Russell, S. & Norvig, P.** — _Artificial Intelligence: A Modern Approach_ (4th Edition). Chapters 3–4 cover uninformed and informed search.
2. **Cormen, T. et al.** — _Introduction to Algorithms_ (CLRS). Chapter 22 covers BFS and DFS on graphs.
3. **Wikipedia** — [Breadth-First Search](https://en.wikipedia.org/wiki/Breadth-first_search), [Depth-First Search](https://en.wikipedia.org/wiki/Depth-first_search), [Bidirectional Search](https://en.wikipedia.org/wiki/Bidirectional_search), [Maze Generation](https://en.wikipedia.org/wiki/Maze_generation_algorithm).

---

_Built as part of the AI Lab coursework. Visualizers are designed to help students understand how search algorithms explore state spaces._
