#!/usr/bin/env python3

# %%
import json
import matplotlib.pyplot as plt

from aray.types import Point
from aray.problem import Problem, Pose

number = 64
problem = Problem.get(number)

hole = problem.hole
cycle = hole + [hole[0]]

plt.plot([c.x for c in cycle], [c.y for c in cycle])
#flip y axis
plt.gca().invert_yaxis()

vertices = problem.vertices

x = 60
y = 205
edges = problem.edges
for a, b in edges:
    v, u = vertices[a], vertices[b]
    plt.plot([v.x + x, u.x + x], [v.y + y, u.y + y])

pose = Pose(vertices=[Point(v.x + x, v.y + y) for v in vertices])

with open(f'/tmp/{number}.solution', 'w') as f:
    json_str = pose.json()
    f.write(json_str)
