import random
import math

def f(x):
    return -x**2 + 5*x + 10

def simulated_annealing(start, temp=1000, cooling_rate=0.95):
    current = start

    while temp > 1:
        neighbor = current + random.uniform(-1, 1)
        delta = f(neighbor) - f(current)

        if delta > 0 or random.random() < math.exp(delta / temp):
            current = neighbor

        temp *= cooling_rate

    return current, f(current)

# Run
x, value = simulated_annealing(start=0)
print("\nSimulated Annealing")
print("Best x:", round(x, 3))
print("Maximum value:", round(value, 3))
