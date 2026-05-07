import random

# Parameter ranges
M_RANGE = (0, 100)
T_RANGE = (10, 50)
L_RANGE = (10, 100)
F_RANGE = (5, 20)

POP_SIZE = 20
GENERATIONS = 100
MUTATION_RATE = 0.1



def fitness(individual):
    M, T, L, F = individual
    
   
    if M < 20 or T > 40 or L < 20 or F < 10:
        return -1000  
  
    return (M * 0.8) + (T * 1.5) + (L * 0.2) + (F * 0.5)



def create_individual():
    return [
        random.uniform(*M_RANGE),
        random.uniform(*T_RANGE),
        random.uniform(*L_RANGE),
        random.uniform(*F_RANGE)
    ]



def selection(population):
    return max(random.sample(population, 3), key=fitness)



def crossover(parent1, parent2):
    point = random.randint(1, 3)
    child = parent1[:point] + parent2[point:]
    return child



def mutate(individual):
    if random.random() < MUTATION_RATE:
        index = random.randint(0, 3)
        
        if index == 0:
            individual[0] = random.uniform(*M_RANGE)
        elif index == 1:
            individual[1] = random.uniform(*T_RANGE)
        elif index == 2:
            individual[2] = random.uniform(*L_RANGE)
        else:
            individual[3] = random.uniform(*F_RANGE)
    
    return individual



population = [create_individual() for _ in range(POP_SIZE)]



for gen in range(GENERATIONS):
    new_population = []
    
    for _ in range(POP_SIZE):
        parent1 = selection(population)
        parent2 = selection(population)
        
        child = crossover(parent1, parent2)
        child = mutate(child)
        
        new_population.append(child)
    
    population = new_population
    
    best = max(population, key=fitness)
    print(f"Generation {gen+1}: Best Fitness = {fitness(best):.2f}")



best_solution = max(population, key=fitness)
print("\nBest Rope Design:")
print(f"Material (M): {best_solution[0]:.2f}")
print(f"Thickness (T): {best_solution[1]:.2f}")
print(f"Length (L): {best_solution[2]:.2f}")
print(f"Twist Factor (F): {best_solution[3]:.2f}")
print(f"Maximum Strength: {fitness(best_solution):.2f}")