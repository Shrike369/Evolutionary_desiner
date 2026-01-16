import subprocess

GENERATIONS = 10  # Set how many generations you want to run

for gen in range(GENERATIONS):
    print(f"\n=== GENERATION {gen+1} ===\n")

    # 1. Generate tires
    print("Running tire_designer.py ...")
    subprocess.run(["python3", "tire_designer.py"], check=True)

    # 2. Run simulation
    print("Running sim_launch_test1.py ...")
    subprocess.run(["python3", "sim_launch_test1.py"], check=True)

    # 3. Run genetic algorithm
    print("Running genetic_algorithm.py ...")
    subprocess.run(["python3", "genetic_algorithm.py"], check=True)

    print(f"=== Generation {gen+1} complete ===\n")

print("All generations complete!")