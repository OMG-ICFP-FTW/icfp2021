#!/usr/bin/env python

# %%
import os
import sys
import json
import random
import matplotlib.pyplot as plt

from aray.problem import Problem
from aray.boxlet import Boxlet
from aray.types import Point


# Path of 'icfp2021' directory
BASE_PATH = base = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.realpath(__file__))))

hole_path = os.path.join(BASE_PATH, 'valid_hole_slots')

# number = random.randint(1, 79)
number = 31

filepath = os.path.join(hole_path, '{}.json'.format(number))

with open(filepath, 'r') as f:
    data = json.load(f)


fig, ax = plt.subplots(figsize=(10,10))

xs = [d[0] for d in data]
ys = [d[1] for d in data]
ax.scatter(xs, ys, s=4)

#  generate random 2d points within [0, 10]
polygon = Problem.get(number).hole
cycle = polygon + [polygon[0]]

ax.plot([c.x for c in cycle], [c.y for c in cycle], 'k-', linewidth=1)


# %%
# tqdm notebook support
from tqdm.notebook import trange
for i in trange(1, 89):
    filepath = os.path.join(hole_path, '{}.json'.format(i))
    with open(filepath, 'r') as f:
        data = json.load(f)
    valid_hole_points = set(Point(*d) for d in data)
    assert len(data) == len(valid_hole_points)
    polygon = Problem.get(i).hole
    boxlet_points = set()
    for boxlet in Boxlet.from_polygon(polygon):
        points = boxlet.iter_points()
        for p in points:
            # assert p not in boxlet_points, f'{p} {boxlet_points}'
            boxlet_points.add(p)
    assert len(boxlet_points) == len(valid_hole_points), f'{i} {len(boxlet_points)} {len(valid_hole_points)}'
    assert boxlet_points == valid_hole_points


# %%
number = 31
filepath = os.path.join(hole_path, '{}.json'.format(number))
with open(filepath, 'r') as f:
    data = json.load(f)
valid_hole_points = set(Point(*d) for d in data)
polygon = Problem.get(i).hole
boxlet_points = set()
for boxlet in Boxlet.from_polygon(polygon):
    points = boxlet.iter_points()
    for p in points:
        # assert p not in boxlet_points, f'{p} {boxlet_points}'
        boxlet_points.add(p)

# assert valid_hole_points == boxlet_points

intersect = valid_hole_points & boxlet_points
valid_only = valid_hole_points - boxlet_points
boxlet_only = boxlet_points - valid_hole_points

fig, ax = plt.subplots(figsize=(10,10))
# plot intersection in grey, valid_only in red, boxlet_only in blue
ax.scatter([p.x for p in intersect], [p.y for p in intersect], s=4, c='grey')
ax.scatter([p.x for p in valid_only], [p.y for p in valid_only], s=4, c='red')
ax.scatter([p.x for p in boxlet_only], [p.y for p in boxlet_only], s=4, c='blue')

print('valid_only', valid_only)
print('boxlet_only', boxlet_only)

# %%
cycle = polygon + [polygon[0]]
edges = [cycle[i:i+2] for i in range(len(cycle)-1)]
# get the edge with the smallest y coordinate
min_y_edge = min(edges, key=lambda e: e[0].y)
min_y_edge