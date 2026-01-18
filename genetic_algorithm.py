"""
Genetic Algorithm for Tire Optimization
Reads fitness_results.json → selects top 2 parents → creates new generation → updates chromosomes.json
"""

import json
import random
import numpy as np

# ==================================================
#  STEP 1 — LOAD FITNESS RESULTS
# ==================================================
with open("cycle_updates/fitness_results.json", "r") as f:
    fitness_results = json.load(f)

print(f" Loaded {len(fitness_results)} fitness results")

# ==================================================
#  STEP 2 — EXTRACT TOP 2 PARENTS
# ==================================================
# Sort by rank (ascending, rank 1 is best)
ranked = sorted(
    [r for r in fitness_results if "rank" in r],
    key=lambda x: x["rank"]
)

if len(ranked) < 2:
    print(" ERROR: Need at least 2 ranked results")
    exit(1)

parent1_env_id = ranked[0]["env_id"]
parent2_env_id = ranked[1]["env_id"]

print(f" Parent 1: env_id {parent1_env_id} (rank {ranked[0]['rank']})")
print(f" Parent 2: env_id {parent2_env_id} (rank {ranked[1]['rank']})")

# ==================================================
#  STEP 3 — LOAD CHROMOSOMES AND SELECT PARENTS
# ==================================================
with open("cycle_updates/chromosomes.json", "r") as f:
    chromosomes = json.load(f)

parent1 = list(chromosomes[parent1_env_id])
parent2 = list(chromosomes[parent2_env_id])

print(f" Parent 1 chromosome: {parent1}")
print(f" Parent 2 chromosome: {parent2}")

# ==================================================
#  STEP 4 — CROSSOVER & MUTATION
# ==================================================
def crossover(p1, p2):
    """Single-point crossover"""
    crossover_point = random.randint(1, len(p1) - 1)
    child = p1[:crossover_point] + p2[crossover_point:]
    
    # Ensure tread_count (index 2) is integer after crossover
    child = list(child)
    child[2] = int(round(child[2]))
    
    return child

def mutate(chromosome, mutation_rate=0.2, mutation_std=0.15):
    """Gaussian mutation with type constraints"""
    mutated = list(chromosome)
    
    for i in range(len(mutated)):
        if random.random() < mutation_rate:
            noise = np.random.normal(0, mutation_std * mutated[i])
            mutated[i] = max(1, mutated[i] + noise)
            
            # Keep tread_count (index 2) as integer
            if i == 2:
                mutated[i] = int(round(mutated[i]))
    
    return mutated

# Generate new population of 10
new_population = []
for i in range(10):
    child = crossover(parent1, parent2)
    child = mutate(child)
    
    # Double-check tread_count (index 2) is integer
    child[2] = int(round(child[2]))
    
    new_population.append(child)
    print(f"  🧬 Offspring {i}: {child}")

# ==================================================
#  STEP 5 — SAVE NEW CHROMOSOMES
# ==================================================
with open("cycle_updates/chromosomes.json", "w") as f:
    json.dump(new_population, f, indent=2)

print(f"\n✔ Updated chromosomes.json with {len(new_population)} new offspring")

# ==================================================
#  STEP 6 — UPDATE GENERATION COUNTER
# ==================================================
try:
    with open("cycle_updates/current_generation.json", "r") as f:
        gen_data = json.load(f)
    current_gen = gen_data.get("generation", 0)
except FileNotFoundError:
    current_gen = 0

next_gen = current_gen + 1
with open("cycle_updates/current_generation.json", "w") as f:
    json.dump({"generation": next_gen}, f, indent=2)

print(f" Updated generation: {current_gen} → {next_gen}")
print(" Genetic algorithm complete!")