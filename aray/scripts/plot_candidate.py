#!/usr/bin/env python3

# %%

import os
import json
import matplotlib.pyplot as plt

from aray.types import Point
from aray.problem import Problem, Pose, BASE_PATH
from aray.boxlet import polygon_points
from aray.stretch import stretch, slow_stretch
from aray.util import dist

problem = Problem.get(38)
# fname = os.path.join(BASE_PATH, 'candidates', '4-9172-cpsolver.json')
fname = '/tmp/38-0-cpsolver2.json'
with open(fname, 'r') as f:
    pose = Pose.from_json(json.load(f))
print('pose', pose)
print('problem', problem)

assert len(problem.vertices) == len(pose.vertices), f'{len(problem.vertices)} {len(pose.vertices)}'

# %%
fig, ax = plt.subplots()

# flip y axis
ax.invert_yaxis()

points = sorted(polygon_points(problem.hole))
ax.scatter([p.x for p in points], [p.y for p in points], c='k', s=1, alpha=0.5)


cycle = problem.hole + [problem.hole[0]]
for i in range(len(cycle) - 1):
    u, v = cycle[i], cycle[i + 1]
    ax.plot([u.x, v.x], [u.y, v.y], 'r-', linewidth=1)

for a, b in problem.edges:
    u, v = pose.vertices[a], pose.vertices[b]
    ax.plot([u.x, v.x], [u.y, v.y], 'b-', linewidth=1)

edge = problem.edges[1]
u, v = pose.vertices[edge[0]], pose.vertices[edge[1]]
d = dist(problem.vertices[edge[0]], problem.vertices[edge[1]])
print('d', d)
ax.plot([u.x, v.x], [u.y, v.y], 'g-')
u_stretch = slow_stretch(problem.vertices[edge[0]], problem.vertices[edge[1]], problem.epsilon)
u_moved = [Point(u.x + us.x, u.y + us.y) for us in u_stretch]
u_moved = [um for um in u_moved if um in points]
ax.scatter([p.x for p in u_moved], [p.y for p in u_moved], s=3)

set(dist(u, p) for p in u_moved)

# sorted(u_moved)

# %%
print('edge', edge)
old_d = dist(problem.vertices[edge[0]], problem.vertices[edge[1]])
print('old_d', old_d)
new_d = dist(pose.vertices[edge[0]], pose.vertices[edge[1]])
print('new_d', new_d)
ratio = abs(new_d / old_d - 1)
print('ratio', ratio)
eps = ratio * 1_000_000
print('epsilon', eps, problem.epsilon)
print('is valid?', eps < problem.epsilon)

# %%
dists = [dist(u, um) for um in u_moved]
print('dists', dists)
ratios = [abs(d / old_d - 1) for d in dists]
print('ratios', ratios)
eps = [r * 1_000_000 for r in ratios]
print('epsilons', eps)
valids = [e < problem.epsilon for e in eps]
print('valids', valids)