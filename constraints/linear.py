import json
import math

with open("problems/1.json") as f:
    p78 = json.loads(f.read())

hole = p78["hole"]
figure_edges = p78["figure"]["edges"]
figure_vertices = p78["figure"]["vertices"]
epsilon = p78["epsilon"]

from ortools.sat.python import cp_model
from shapely.geometry import Polygon, Point, LineString

model = cp_model.CpModel()

# Hole Bounding box
hole_min_x = min([p[0] for p in hole])
hole_max_x = max([p[0] for p in hole])
hole_min_y = min([p[1] for p in hole])
hole_max_y = max([p[1] for p in hole])
print(f"Hole x={hole_min_x}:{hole_max_x} y={hole_min_y}:{hole_max_y}")

sh_hole = Polygon(hole)
sh_hole_linestring = sh_hole.exterior
allowed_positions = []
for x in range(hole_min_x, hole_max_x):
  for y in range(hole_min_y, hole_max_y):
    if sh_hole.contains(Point(x, y)):
      allowed_positions.append((x, y))
        # print(f"{x},{y} in hold= {sh_hole.contains(Point(x, y))}")
print(f"Hole possible locations {len(allowed_positions)} / {(hole_max_x - hole_min_x) * (hole_max_y - hole_min_y)}")

# Create model variables for each pose vertex
pose_vertexes = {}
for i, v in enumerate(figure_vertices):
  pose_vertexes[i] = (
    model.NewIntVar(hole_min_x, hole_max_x, f'{i}_x'),
    model.NewIntVar(hole_min_y, hole_max_y, f'{i}_y')
  )

# Create a map of all possible starting and ending x,y for each edge
print(f"Total edges {len(figure_edges)}")
for i, edge in enumerate(figure_edges):
  print(f"Creating map for edge {i}")
  vertex = figure_vertices[edge[0]]
  v2 = figure_vertices[edge[1]]
  distance = math.hypot(v2[0] - vertex[0], v2[1] - vertex[0])

  allowed_assignments = []
  for p1 in allowed_positions:
    for p2 in allowed_positions:
      if math.hypot(p2[0] - p1[0], p2[1] - p1[1]) / distance -1 <= (epsilon / 1000000):
        # check if the line collides with the hole
        sh_edge = LineString([p1, p2])
        if not sh_edge.intersection(sh_hole_linestring):
          allowed_assignments.append((p1[0], p1[1], p2[0], p2[1]))

  model.AddAllowedAssignments([
      pose_vertexes[edge[0]][0],
      pose_vertexes[edge[0]][1],
      pose_vertexes[edge[1]][0],
      pose_vertexes[edge[1]][1]
    ], allowed_assignments)

  print(f"{i}: ({edge[0]}) {vertex} -> ({edge[1]}) {v2} with distance {distance} has {len(allowed_assignments)} allowed assignments")

# Add optimization criteria
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
  print(f"Optimal or Feasible")
  for i, v in pose_vertexes.items():
    print(f"{i}: {solver.Value(v[0]), solver.Value(v[1])}")
else:
  print(f":(")
