#!/usr/bin/env python3

# %%

import os
import json
import matplotlib.pyplot as plt

from aray.problem import Problem, Pose, BASE_PATH

problem = Problem.get(4)
fname = os.path.join(BASE_PATH, 'candidates', '4-9172-cpsolver.json')
with open(fname, 'r') as f:
    pose = Pose.from_json(json.load(f))
print(pose)
print(problem)

# %%
fig, ax = plt.subplots()

# flip y axis
ax.invert_yaxis()

for a, b in problem.edges:
    u, v = pose.vertices[a], pose.vertices[b]
    ax.plot([u.x, v.x], [u.y, v.y], 'b-')

cycle = problem.hole + [problem.hole[0]]
for i in range(len(cycle) - 1):
    u, v = cycle[i], cycle[i + 1]
    ax.plot([u.x, v.x], [u.y, v.y], 'r-')