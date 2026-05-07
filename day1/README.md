# Maze Route Finder Visualizer

This project contains two Python GUI apps that show how search algorithms work step by step.

## Files

- [maze_solver.py](maze_solver.py) visualizes maze solving with **BFS** and **DFS**.
- [route_finder.py](route_finder.py) visualizes **bidirectional search** on a graph.

## How the maze solver works

The maze solver explores a 2D grid where `0` means open path and `1` means wall.

### BFS

Breadth-first search explores the maze level by level.

Step by step:

1. Put the start cell into a queue.
2. Remove the first cell from the queue.
3. Mark it as visited.
4. Add all unvisited open neighbors to the queue.
5. Repeat until the goal is found or no cells remain.

Why BFS matters:

- It finds the shortest path in an unweighted maze.
- It is usually the best choice when you care about minimum steps.

### DFS

Depth-first search explores one branch as far as it can before backtracking.

Step by step:

1. Put the start cell on a stack.
2. Remove the most recent cell from the stack.
3. Mark it as visited.
4. Push all unvisited open neighbors onto the stack.
5. Repeat until the goal is found or all branches are exhausted.

Why DFS matters:

- It is useful for understanding full exploration.
- It does not guarantee the shortest path.

## How bidirectional search works

Bidirectional search runs two searches at the same time:

- one forward from the start
- one backward from the goal

Step by step:

1. Start one frontier at the source node.
2. Start another frontier at the target node.
3. Expand one step from each side.
4. Track visited nodes and parent links on both sides.
5. Stop when both searches meet at the same node.
6. Combine the two partial paths into one final route.

Why this helps:

- It often explores fewer nodes than a one-direction search.
- It is especially useful when the graph is large and the start/goal are far apart.

## GUI features

- Uses a Python Tkinter interface for both apps.
- Shows the active frontier, visited nodes, current node, and final route.
- Animates each search step so you can follow the flow visually.
- Includes an expandable search log that explains what the algorithm is doing.
- Fully scrollable control panels to comfortably fit on smaller displays.
- Lets you interact with the maze by clicking cells to add or remove walls.
- Lets you choose start and goal nodes in the route finder.

## How to run

```powershell
python maze_solver.py
python route_finder.py
```

## Maze solver controls

- Select **BFS** for shortest-path search.
- Select **DFS** for deep branch exploration.
- Click **Run Search** to animate the algorithm.
- Click **Generate Tree Maze** to randomly generate a perfect maze using recursive backtracking.
- Click **Load Sample Maze** to restore the built-in grid.
- Click **Clear Maze** to start from an empty maze and draw your own walls.

## Route finder controls

- Choose a start node and a goal node.
- Click **Run Search** to animate the bidirectional search.
- Click **Load Sample Graph** to restore the default graph.
- Click **Random** to generate a randomized graph layout and connections.
- Click **Clear** to completely clear the canvas.
- Drag the **New Node** card onto the canvas to create a new node.
- Drag an existing node inside the canvas to move it.
- **Double-click** a node to delete it and any attached connections.
- **Right-click and drag** between two nodes to manually connect them, or to disconnect an existing connection.
- When a dropped or moved node is close enough to another node, the app connects them automatically.

## Color guide

- Maze start: yellow
- Maze goal: red
- Maze frontier: blue
- Maze visited cells: light blue
- Maze final path: green
- Route finder start: orange
- Route finder goal: red
- Forward search nodes: blue
- Backward search nodes: pink
- Meeting node: green
- Final route: gold

## Notes

- Start and goal positions are fixed in the maze solver.
- The route finder uses a small built-in graph so the search flow is easy to understand.
- Both apps are written in Python, so the project stays simple to run and edit.