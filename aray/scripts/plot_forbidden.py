#!/usr/bin/env python

# %%
import matplotlib.pyplot as plt
from aray.types import Pair, Point
from aray.forbidden import forbidden
from aray.problem import Problem
from aray.boxlet import polygon_points

problem = Problem.get(1)

vertices = problem.vertices
edges = [Pair(vertices[a], vertices[b]) for a, b in problem.edges]
# edges = [Pair(Point(0, 0), Point(0, 5))]
forbidden_edges = forbidden(problem.hole, edges, problem.epsilon)


points = list(polygon_points(problem.hole))
plt.scatter([p.x for p in points], [p.y for p in points], s=1)

for pairs in forbidden_edges:
    for a, b in pairs:
        plt.plot([a.x, b.x], [a.y, b.y], 'b-', linewidth=0.5)

cycle = problem.hole + [problem.hole[0]]
plt.plot([c.x for c in cycle], [c.y for c in cycle], 'r-', linewidth=0.5)

# flip y axis
plt.gca().invert_yaxis()
