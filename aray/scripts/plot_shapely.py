#!/usr/bin/env python3
# plot_shapely.py

# %%
from dataclasses import dataclass
from typing import List, Tuple, Set
import matplotlib.pyplot as plt

from aray.problem import Problem

from shapely.geometry import Polygon, Point, LineString

'''
Datastructures we want to have

point: integer pair, not the shapely kind
delta: integer pair, difference between two points
edge: integer pair, indexes into a point or vertex list
segment: point pair

problem data:
hole: list of points (form a polygon)
vertices: list of points
edges: list of edges, indexes into vertices

computed data:
points: sorted list of valid points
edge_dists: list of edge distances, corresponds to edges
dist_deltas: map from dist to a list of deltas
delta_forbidden: map from delta to a list of forbidden segments



'''


# %%
def get_points(hole):
    poly = Polygon(hole)
    min_x, min_y, max_x, max_y = poly.bounds
    points = []
    for x in range(int(min_x), int(max_x) + 1):
        for y in range(int(min_y), int(max_y) + 1):
            if poly.intersects(Point(x, y)):
                points.append((x, y))
    return sorted(points)


def get_forbidden(hole, delta):
    poly = Polygon(hole)
    forbidden = []
    for a in points:
        b = (a[0] + delta[0], a[1] + delta[1])
        if b not in points:
            continue
        ab = LineString((a, b))
        if poly.contains(ab) or ab.within(poly):
            continue
        elif poly.exterior.crosses(ab):
            forbidden.append((a, b))
        elif poly.touches(ab) and not poly.exterior.contains(ab):
            forbidden.append((a, b))
    return forbidden


def get_deltas(d_old: int, epsilon: int) -> List[Tuple[int, int]]:
    deltas = []
    n = int(d_old ** 0.5 + 1) * 2
    for x in range(-n, n + 1):
        for y in range(-n, n + 1):
            d_new = dsq((0, 0), (x, y))
            if abs(d_new / d_old - 1) <= epsilon / 1e6:
                deltas.append((x, y))
    return deltas


fig, ax = plt.subplots()
problem = Problem.get(14)
problem.plot(fig, ax)


points = get_points(problem.hole)
xs = [p[0] for p in points]
ys = [p[1] for p in points]
ax.scatter(xs, ys)

forbidden = get_forbidden(problem.hole, (-1, -1))
for a, b in forbidden:
    ax.plot((a[0], b[0]), (a[1], b[1]))
forbidden

# %%

problem = Problem.get(14)
vert = problem.vertices
def dsq(a, b): return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2


edge_dsq = [dsq(vert[i], vert[j]) for i, j in problem.edges]

epsilon = problem.epsilon
for d_old in sorted(set(edge_dsq)):
    print(d_old, edge_dsq.count(d_old))
    deltas = get_deltas(d_old, epsilon)
    print('d', deltas)
    fig, ax = plt.subplots()
    ax.grid(True)
    # set x and y ticks
    ax.set_xticks(range(-n, n + 1))
    ax.set_yticks(range(-n, n + 1))
    ax.scatter([p[0] for p in deltas], [p[1] for p in deltas])
