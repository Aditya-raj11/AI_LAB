# Assignment 11: Hill Climbing for AI Search Problems
# Problem: N-Queens (8x8)
# Variants: Simple HC, Steepest Ascent HC, Random Restart HC

import random

N = 8  # board size


# ── State & Fitness ──────────────────────────────
def random_state():
    return [random.randint(0, N-1) for _ in range(N)]

def fitness(state):
    """Count non-attacking pairs (higher is better). Max = 28."""
    attacks = 0
    for i in range(N):
        for j in range(i+1, N):
            if state[i] == state[j] or abs(state[i]-state[j]) == abs(i-j):
                attacks += 1
    return N*(N-1)//2 - attacks

def get_neighbors(state):
    """All states from moving one queen."""
    neighbors = []
    for row in range(N):
        for col in range(N):
            if col != state[row]:
                s = list(state)
                s[row] = col
                neighbors.append(s)
    return neighbors


# ── Simple Hill Climbing ─────────────────────────
def simple_hc(state):
    current = list(state)
    history = [fitness(current)]
    while True:
        improved = False
        for nb in get_neighbors(current):
            if fitness(nb) > fitness(current):
                current = nb
                history.append(fitness(current))
                improved = True
                break
        if not improved:
            break
    return current, history


# ── Steepest Ascent Hill Climbing ────────────────
def steepest_hc(state):
    current = list(state)
    history = [fitness(current)]
    while True:
        neighbors = get_neighbors(current)
        best = max(neighbors, key=fitness)
        if fitness(best) <= fitness(current):
            break
        current = best
        history.append(fitness(current))
    return current, history


# ── Random Restart Hill Climbing ─────────────────
def random_restart_hc(max_restarts=20):
    best, best_fit = None, 0
    all_histories = []
    for _ in range(max_restarts):
        init = random_state()
        result, history = steepest_hc(init)
        all_histories.append(history)
        if fitness(result) > best_fit:
            best_fit = fitness(result)
            best = result
        if best_fit == N*(N-1)//2:
            break
    return best, all_histories


# ── Run ──────────────────────────────────────────
random.seed(42)
init = random_state()
MAX_FIT = N * (N-1) // 2

r1, h1 = simple_hc(init)
r2, h2 = steepest_hc(init)
r3, all_h3 = random_restart_hc()

print(f"Initial  fitness: {fitness(init)}/{MAX_FIT}")
print(f"Simple HC        fitness: {fitness(r1)}/{MAX_FIT}  | Solved: {fitness(r1)==MAX_FIT}")
print(f"Steepest HC      fitness: {fitness(r2)}/{MAX_FIT}  | Solved: {fitness(r2)==MAX_FIT}")
print(f"Random Restart   fitness: {fitness(r3)}/{MAX_FIT}  | Solved: {fitness(r3)==MAX_FIT}")
