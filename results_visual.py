import json
import matplotlib.pyplot as plt

NUM_GENERATIONS = 20  # Edit as needed

with open("cycle_updates/fitness_history.json", "r") as f:
    history = json.load(f)

generations = []
best_steps = []
best_distances = []

for gen in history[:NUM_GENERATIONS]:
    generations.append(gen["generation"])
    # Find the best (lowest) finish step and its distance
    finished = [r for r in gen["results"] if r["finished"] and r["finish_step"] is not None]
    if finished:
        best = min(finished, key=lambda r: r["finish_step"])
        best_steps.append(best["finish_step"])
        best_distances.append(best["distance"])
    else:
        best_steps.append(None)
        best_distances.append(None)

plt.plot(generations, best_steps, marker='o', color='purple', label="Best Finish Step")
for x, y, d in zip(generations, best_steps, best_distances):
    if y is not None:
        plt.text(x, y, f"{d:.2f}", fontsize=8, ha='center', va='bottom')

plt.xlabel("Generation")
plt.ylabel("Best Finish Step (Time)")
plt.title("Best Finish Step per Generation (Distance as label)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.gca().invert_yaxis()  # Invert y-axis so improvement goes up
plt.show()