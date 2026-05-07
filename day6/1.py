def f(x):
    return -x**2 + 5*x + 10

def steepest_ascent(start, step=0.1, max_iter=100):
    current = start

    for i in range(max_iter):
        neighbors = [current - step, current + step]
        best_neighbor = max(neighbors, key=f)

        if f(best_neighbor) <= f(current):
            break

        current = best_neighbor

    return current, f(current)

# Run
x, value = steepest_ascent(start=0)
print("Steepest Ascent Hill Climbing")
print("Best x:", round(x, 3))
print("Maximum value:", round(value, 3))
