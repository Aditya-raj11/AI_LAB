import random

def f(x):
    return -x**2 + 5*x + 10

def stochastic_hill(start, step=0.1, max_iter=100):
    current = start

    for i in range(max_iter):
        neighbor = current + random.choice([-step, step])
        if f(neighbor) > f(current):
            current = neighbor

    return current, f(current)

# Run
x, value = stochastic_hill(start=0)
print("\nStochastic Hill Climbing")
print("Best x:", round(x, 3))
print("Maximum value:", round(value, 3))
