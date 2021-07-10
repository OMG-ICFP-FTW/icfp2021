#!/usr/bin/env python
# boxlet.py - Boxlet class and utilities

# %%
import matplotlib.pyplot as plt
import random
from math import floor, ceil
from collections import namedtuple, defaultdict
from dataclasses import dataclass
from typing import List, Optional, Tuple, Union

from aray.types import Point, Quad
from aray.intersect import intersections, intersection, maybe_intersection
from aray.partition import partition
from aray.problem import Problem

#  generate random 2d points within [0, 10]
# polygon = [Point(random.randint(0, 10), random.randint(0, 10))
#            for _ in range(4)]
# polygon = [Point(10, 0), Point(0, 10), Point(10, 10), Point(4, 8)]
number = random.randint(1,79)
polygon = Problem.get(number).hole

M = max(p.x for p in polygon)
N = max(p.y for p in polygon)

fig, ax = plt.subplots()
ax.set_xlim(-1, M)
ax.set_ylim(-1, N)
ax.set_xticks(range(M))
ax.set_yticks(range(N))
ax.grid(which='major', axis='x', linewidth=0.75, color='k', alpha=0.1)
ax.grid(which='major', axis='y', linewidth=0.75, color='k', alpha=0.1)
ax.set_aspect('equal')

cycle = polygon + [polygon[0]]
ax.plot([c.x for c in cycle], [c.y for c in cycle], 'k:')

def plot_quad(quad, ax):
    """ Plot a quad """
    points = [quad.bottom_left, quad.bottom_right, quad.top_right, quad.top_left, quad.bottom_left]
    # plot filled in polygon
    xs = [p.x for p in points]
    ys = [p.y for p in points]
    ax.fill(xs, ys, alpha=0.5)
    # also plot the edges with points
    ax.plot(xs, ys, 'ko-', linewidth=0.5)


quads = partition(polygon)
# print('quads', quads)
for quad in quads:
    # print('plotting quad', quad)
    plot_quad(quad, ax)
