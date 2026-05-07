import heapq

# -----------------------------
# Goal State
# -----------------------------
GOAL_STATE = (1, 2, 3,
              4, 5, 6,
              7, 8, 0)

# -----------------------------
# Valid Moves for Each Position
# -----------------------------
MOVES = {
    0: [1, 3],
    1: [0, 2, 4],
    2: [1, 5],
    3: [0, 4, 6],
    4: [1, 3, 5, 7],
    5: [2, 4, 8],
    6: [3, 7],
    7: [4, 6, 8],
    8: [5, 7]
}

# -----------------------------
# Uniform Cost Search Algorithm
# -----------------------------
def uniform_cost_search(start_state):
    priority_queue = []
    heapq.heappush(priority_queue, (0, start_state, []))
    visited = set()
    nodes_explored = 0

    while priority_queue:
        cost, current_state, path = heapq.heappop(priority_queue)

        if current_state in visited:
            continue

        visited.add(current_state)
        nodes_explored += 1

        if current_state == GOAL_STATE:
            return cost, path + [current_state], nodes_explored

        blank_index = current_state.index(0)

        for move in MOVES[blank_index]:
            new_state = list(current_state)
            new_state[blank_index], new_state[move] = new_state[move], new_state[blank_index]
            new_state = tuple(new_state)

            if new_state not in visited:
                heapq.heappush(
                    priority_queue,
                    (cost + 1, new_state, path + [current_state])
                )

    return None, None, nodes_explored


# -----------------------------
# Heuristic H1: Misplaced Tiles
# -----------------------------
def h1_misplaced_tiles(state):
    return sum(
        1 for i in range(9)
        if state[i] != 0 and state[i] != GOAL_STATE[i]
    )

# -----------------------------
# Heuristic H2: Manhattan Distance
# -----------------------------
def h2_manhattan_distance(state):
    distance = 0
    for i in range(9):
        if state[i] != 0:
            goal_index = GOAL_STATE.index(state[i])
            distance += abs(i // 3 - goal_index // 3) + abs(i % 3 - goal_index % 3)
    return distance


# -----------------------------
# Print Puzzle State
# -----------------------------
def print_state(state):
    for i in range(0, 9, 3):
        print(state[i:i+3])
    print()


# -----------------------------
# Main Execution
# -----------------------------
if __name__ == "__main__":

    start_state = (1, 2, 3,
                   4, 0, 5,
                   6, 7, 8)

    print("Initial State:")
    print_state(start_state)

    cost, solution_path, nodes = uniform_cost_search(start_state)

    print("Goal State:")
    print_state(GOAL_STATE)

    print("Solution Depth (Cost):", cost)
    print("Nodes Explored:", nodes)

    print("\nHeuristic Comparison (Not Used in UCS):")
    print("H1 - Misplaced Tiles:", h1_misplaced_tiles(start_state))
    print("H2 - Manhattan Distance:", h2_manhattan_distance(start_state))

    print("\nSolution Path:")
    for step, state in enumerate(solution_path):
        print(f"Step {step}:")
        print_state(state)
