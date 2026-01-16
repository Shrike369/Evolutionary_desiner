"""
Batch CadQuery Tire Generator
Generates 10 tires → tire_0.stl … tire_9.stl
Reads chromosomes from chromosomes.json
"""

import json
import cadquery as cq
from cadquery import exporters

# ==================================================
# 🔥 STEP 1 — LOAD CHROMOSOMES FROM JSON
# ==================================================
with open("cycle_updates/chromosomes.json", "r") as f:
    chromosomes = json.load(f)

print(f"📋 Loaded {len(chromosomes)} chromosomes from chromosomes.json")

# ==================================================
# CONSTANT INNER DIAMETER (STATIC DESIGN RULE!)
# ==================================================
inner_radius = 20.0  # Do NOT change, stays constant

fillet_radius = 4.0
tread_axial_width = 40.0  # stays constant unless you want GA control

# ==================================================
# 🚀 STEP 2 — LOOP AND GENERATE 10 STL FILES
# ==================================================
for idx, (outer_radius, tire_axial_width, tread_count, tread_width, tread_depth) in enumerate(chromosomes):

    print(f"🛞 Generating Tire {idx} …")

    half_width = tire_axial_width / 2.0

    # Tire body profile
    profile_points = [
        (inner_radius, -half_width),
        (inner_radius, half_width),
        (outer_radius, half_width),
        (outer_radius, -half_width),
        (inner_radius, -half_width),
    ]

    tire = (
        cq.Workplane("XZ")
        .polyline(profile_points)
        .close()
        .revolve(360)
    )

    # Optional safety fillet
    try:
        tire = tire.edges().fillet(fillet_radius)
    except:
        pass

    # Treads
    grooves = None
    groove_angle = 360.0 / tread_count

    for i in range(tread_count):
        angle = i * groove_angle
        single = (
            cq.Workplane("XY")
            .box(tread_depth, tread_width, tread_axial_width, centered=(True, True, True))
            .translate((outer_radius - tread_depth/2.0, 0, 0))
            .rotate((0,0,0), (0,0,1), angle)
        )
        grooves = single if grooves is None else grooves.union(single)

    final = tire.cut(grooves)

    # Export STL + STEP
    stl_name = f"robot/tire_{idx}.stl"
    

    exporters.export(final, stl_name)
    

    print(f"   ✔ {stl_name} created")

print("\n🎉 DONE — 10 tire files generated!")
print("Use tire_0.stl … tire_9.stl inside Genesis")
