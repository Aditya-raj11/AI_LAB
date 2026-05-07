import random
material_min_p = 0
material_max_p = 100
thickness_min = 10
thickness_max = 50
length_min = 10
length_max = 100
twist_min = 5
twist_max = 20


def create_individual():
    return {
        "M": random.uniform(material_min_p, material_max_p),
        "T": random.uniform(thickness_min, thickness_max),
        "L": random.uniform(length_min, length_max),
        "F": random.uniform(twist_min, twist_max),
    }

def fitness(ind):

    return (ind["M"]* 0.8) + (ind["T"] * 1.5) + (ind["L"] * 0.2) + (ind["F"] * 0.5)




