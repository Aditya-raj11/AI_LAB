# AI Lab Day 5 Report

**Date:** 2026-01-22
**Topic:** Search Algorithms (BFS, DFS, UCS, A*)

---

## Assignment 6: Robot Path Planning

### Problem Statement
Implement and compare Search Algorithms (BFS, UCS, A*) to find a path for a robot in a grid environment with obstacles. Use Manhattan and Euclidean distance heuristics.

### Implementation Details
- **Grid Size:** 10x10
- **Start:** (0, 0)
- **Goal:** (9, 9)
- **Obstacles:** Defined in `grid` array.
- **Algorithms:**
    1.  **BFS:** Breadth-First Search (Unweighted).
    2.  **UCS:** Uniform Cost Search.
    3.  **A* (Manhattan):** A* with Manhattan distance ($|x_1-x_2| + |y_1-y_2|$).
    4.  **A* (Euclidean):** A* with Euclidean distance ($\sqrt{(x_1-x_2)^2 + (y_1-y_2)^2}$).

### Python Code
The implementation is saved in `assignment6_robot_path.py`. It uses `matplotlib` for real-time animation of the pathfinding.

### Results
| Algorithm | Path Cost/Length | Nodes Explored |
| :--- | :--- | :--- |
| **BFS** | 19 | 67 |
| **UCS** | 18.0 | 67 |
| **A* (Manhattan)** | 18.0 | 63 |
| **A* (Euclidean)** | 16.24 | 64 |

*Note: A* with Euclidean distance found a shorter path (16.24) by moving diagonally, which was allowed for that specific test case.*

---

## Assignment 7: Snake and Ladder AI

### Problem Statement
Implement an AI agent to play the Snake and Ladder game using BFS, DFS, and A* search algorithms to find the optimal path to the goal (100).

### Implementation Details
- **Board:** 1 to 100.
- **Goal:** Reach 100 exactly.
- **Rules:** Snakes move players down, Ladders move players up.
- **Heuristic (A*):** $\lceil (100 - current\_position) / 6 \rceil$ (Minimum dice rolls needed).

### Python Code
The implementation is saved in `assignment7_snake_ladder.py`. It simulates the board game and animates the token movement.

### Results
| Algorithm | Key Characteristic | Moves to Win | Nodes Explored |
| :--- | :--- | :--- | :--- |
| **BFS** | Optimal (Shortest Path) | 7 | 79 |
| **DFS** | Non-Optimal (Deep Search) | 8-24 (Varies) | ~25 |
| **A*** | Optimal & Efficient | 7 | ~11 |

*Observations:*
- **BFS** guarantees the shortest path (minimum dice rolls).
- **A*** also finds the shortest path but explores significantly fewer nodes (11 vs 79) because of the heuristic.
- **DFS** finds a path but it is often much longer and not optimal.

---

## Conclusion
- **A*** is generally the most efficient algorithm for pathfinding when a good heuristic is available.
- **BFS** is reliable for unweighted shortest paths but explores more nodes.
- **DFS** is not suitable for optimal pathfinding but consumes less memory.
