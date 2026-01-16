#!/usr/bin/env python3
import numpy as np
import genesis as gs
import json

# --- 1. Configuration ---
NUM_ENVS = 10
URDF_TEMPLATE = "robot/amr{}.urdf"

TERRAIN_FILE = "robo_world/terrain.stl"
ENV_X_OFFSET = 30.0
ROBOT_START_Z = 1.0 

# --- 2. Control Parameters ---
TARGET_RPM = 100.0  
# Convert RPM to radians per second: (RPM * 2 * pi) / 60
TARGET_VEL = -((TARGET_RPM * 2 * np.pi) / 60.0)

# Initialize Genesis (Using CPU as per your logs)
gs.init(backend=gs.cpu)

# Scene setup
scene = gs.Scene(
    sim_options=gs.options.SimOptions(
        dt=0.03,
        substeps=10, 
    ),
    show_viewer= False
)

# Material physics
terrain_mat = gs.materials.Rigid(friction=0.9)
tire_mat = gs.materials.Rigid(friction=0.09)



robots = []
for i in range(NUM_ENVS):
    env_origin_x = i * ENV_X_OFFSET

    # Ground Plane
    scene.add_entity(morph=gs.morphs.Plane(pos=[env_origin_x, 0, 0], fixed=True))

    # Terrain Mesh
    scene.add_entity(
        morph=gs.morphs.Mesh(
            file=TERRAIN_FILE,
            fixed=True,
            pos=[env_origin_x, 0, 0],
            convexify=False
        ),
        material=terrain_mat,
    )

    # AMR Robot
    amr = scene.add_entity(
        morph=gs.morphs.URDF(
            file=URDF_TEMPLATE.format(i),
            fixed=False,
            pos=[env_origin_x + -1, 0, ROBOT_START_Z] 
        ),
        material=tire_mat,
    )
    robots.append(amr)

scene.build()

# --- 3. Motor and Joint Configuration (Official v0.3.10 Style) ---
wheel_names = [
    "left_front_shaft_to_tire", "left_rear_shaft_to_tire",
    "right_front_shaft_to_tire", "right_rear_shaft_to_tire"
]

for amr in robots:
    # Official API: Use .dof_idx_local to map joint names to simulator indices
    dofs_idx = [amr.get_joint(name).dof_idx_local for name in wheel_names]
    
    # Official API: Set gains
    # For constant velocity, we set kp to 0 and kv to a high value
    amr.set_dofs_kp(kp=np.zeros(4), dofs_idx_local=dofs_idx)
    amr.set_dofs_kv(kv=np.array([1000.0] * 4), dofs_idx_local=dofs_idx)
    
    # Official API: Set force range for motor strength
    amr.set_dofs_force_range(
        lower=np.array([-500.0] * 4), 
        upper=np.array([500.0] * 4), 
        dofs_idx_local=dofs_idx
    )

print(f"🚀 Simulation starting! Constant RPM: {TARGET_RPM}")



# --- 4. Simulation Loop (record finish + position) ---

FINISH_LINE_X = -10.0
finish_step = {env_i: None for env_i in range(NUM_ENVS)}
final_x_pos = {env_i: 0.0 for env_i in range(NUM_ENVS)}

for step in range(400):
    for env_i, amr in enumerate(robots):
        # Re-identify local indices for the control command
        dofs_idx = [amr.get_joint(name).dof_idx_local for name in wheel_names]

        amr.control_dofs_velocity(np.array([TARGET_VEL] * 4), dofs_idx)

        # Monitor the actual RPM every 100 steps
        if step % 100 == 0:
            actual_vels = amr.get_dofs_velocity(dofs_idx)
            actual_rpm = (actual_vels[0] * 60) / (2 * np.pi)
            print(f"Step {step:4d} | Target: {TARGET_RPM:.1f} RPM | Actual: {actual_rpm:.1f} RPM")

        # --- Track robot position + detect first crossing ---
        pos = amr.get_pos()
        env_offset = np.array([env_i * ENV_X_OFFSET, 0, 0])
        pos_local = pos - env_offset
        x = pos_local[0]

        final_x_pos[env_i] = x

        if finish_step[env_i] is None and x <= FINISH_LINE_X:
            finish_step[env_i] = step

    if step % 5 == 0:
        for env_i, amr in enumerate(robots):
            pos = amr.get_pos()
            env_offset = np.array([env_i * ENV_X_OFFSET, 0, 0])
            pos_local = pos - env_offset
            print(f"Step {step:4d} | Env {env_i} | Local Pos = ({pos_local[0]:.2f}, {pos_local[1]:.2f}, {pos_local[2]:.2f})")

    scene.step()

# --- 5. Compute Final Ranking Just Like a Race ---

finishers = [(env, finish_step[env], final_x_pos[env])
             for env in finish_step if finish_step[env] is not None]

non_finishers = [(env, final_x_pos[env])
                 for env in finish_step if finish_step[env] is None]

# Finishers by earliest finish step
finishers_sorted = sorted(finishers, key=lambda x: x[1])

# Non-finishers by farthest distance
non_finishers_sorted = sorted(non_finishers, key=lambda x: x[1], reverse=True)

final_ranking = finishers_sorted + non_finishers_sorted

# --- Print final table ---
print("\n=== FINAL RESULTS ===")
for rank, data in enumerate(final_ranking, start=1):
    if len(data) == 3:
        env, step_finished, dist = data
        print(f"{rank}. Env {env} | FINISHED at step {step_finished} | dist={dist:.3f}")
    else:
        env, dist = data
        print(f"{rank}. Env {env} | NOT finished | dist={dist:.3f}")

# --- Save final ranking to JSON in race order ---
ranked_list = []
for rank, data in enumerate(final_ranking, start=1):
    if len(data) == 3:
        env, step_finished, dist = data
        ranked_list.append({
            "rank": rank,
            "env_id": env,
            "finished": True,
            "finish_step": step_finished,
            "distance": float(dist)
        })
    else:
        env, dist = data
        ranked_list.append({
            "rank": rank,
            "env_id": env,
            "finished": False,
            "finish_step": None,
            "distance": float(dist)
        })

with open("cycle_updates/fitness_results.json", "w") as f:
    json.dump(ranked_list, f, indent=2)


print("Saved fitness_results.json!")
print("🏁 Done!")
