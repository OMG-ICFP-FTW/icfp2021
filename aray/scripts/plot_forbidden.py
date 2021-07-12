#!/usr/bin/env python

# %%
import os
import json
import matplotlib.pyplot as plt
from aray.types import Pair, Point
from aray.forbidden import get_forbidden
from aray.problem import Problem
from aray.boxlet import polygon_points

problem_number = 19
problem = Problem.get(problem_number)

vertices = problem.vertices
edges = [Pair(vertices[a], vertices[b]) for a, b in problem.edges]
forbidden_edges = get_forbidden(problem_number)

# %%
points = list(polygon_points(problem.hole))
plt.scatter([p.x for p in points], [p.y for p in points], s=1)

for pairs, _ in zip(forbidden_edges, range(1000)):
    for (a, b), _ in zip(pairs, range(1000)):
        plt.plot([a.x, b.x], [a.y, b.y], 'b-', linewidth=0.5)

cycle = problem.hole + [problem.hole[0]]
plt.plot([c.x for c in cycle], [c.y for c in cycle], 'r-', linewidth=0.5)

# flip y axis
plt.gca().invert_yaxis()
