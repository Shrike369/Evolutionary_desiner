# Evolutionary Tire Designer

This project uses a genetic algorithm to optimize robot tire designs for simulated performance. It automates tire generation, simulation, and evolutionary improvement, tracking results over generations.

## Features

- **Parametric Tire Generation:** Uses CadQuery to create tire models from chromosome data.
- **Physics Simulation:** Runs each design in a Genesis-based simulation environment.
- **Evolutionary Optimization:** Selects top performers, applies crossover and mutation, and iterates.
- **Result Visualization:** Plots the evolution of best performance over generations.

## Project Structure

- `tire_designer.py` — Generates tire STL files from chromosome data.
- `sim_launch_test1.py` — Runs simulation, records finish steps and distances, saves results.
- `genetic_algorithm.py` — Selects top chromosomes, creates new generation, updates files.
- `launch_pipeline.py` — Automates the full pipeline for multiple generations.
- `results_visual.py` — Plots best finish step per generation.
- `cycle_updates/` — Stores chromosomes, fitness results, and history.
- `robot/` — Contains URDFs and generated tire STL files.
- `robo_world/` — Contains terrain STL.

## Usage

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the pipeline for multiple generations:**
   ```bash
   python3 launch_pipeline.py
   ```

3. **Visualize results:**
   ```bash
   python3 results_visual.py
   ```

## Data Files

- `cycle_updates/chromosomes.json` — Chromosome data for each tire.
- `cycle_updates/fitness_results.json` — Results for the current generation.
- `cycle_updates/fitness_history.json` — All generations' results.
- `cycle_updates/current_generation.json` — Tracks current generation number.

## Customization

- **Tire parameter limits:** Edit `tire_designer.py` to set width/diameter limits.
- **Simulation steps and finish line:** Edit `sim_launch_test1.py`.
- **Genetic algorithm parameters:** Edit mutation/crossover in `genetic_algorithm.py`.

## Requirements

See `requirements.txt` for Python dependencies.

## License

MIT License (or specify your own)
