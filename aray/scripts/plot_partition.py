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
number = random.randint(1, 79)
polygon = Problem.get(number).hole
# polygon = [Point(x=0.9777859405780998, y=7.931598295985899),
#  Point(x=6.095741485892159, y=7.912919084690875),
#  Point(x=5.523774597615163, y=4.099890753524409),
#  Point(x=4.915330592635722, y=7.8768037617591355)]
# polygon = [Point(x=2.7211796489261006, y=7.606768544504109),
#  Point(x=8.66436658931826, y=9.238654894097543),
#  Point(x=3.9793588430828732, y=5.920407912946276),
#  Point(x=2.7852902459037363, y=1.6504715885934695)]
polygon = [
    Point(x=9.693333075533236, y=8.574094317283144),
    Point(x=6.8962708682948906, y=2.079121151343535),
    Point(x=6.7811967452339195, y=6.595001343455414),
    Point(x=3.9014617340203808, y=9.84642920917412)]


M = max(int(max(p.x for p in polygon) + 1), 10)
N = max(int(max(p.y for p in polygon) + 1), 10)

fig, ax = plt.subplots()
ax.set_xlim(-1, M)
ax.set_ylim(-1, N)
ax.set_xticks(range(M))
ax.set_yticks(range(N))
ax.grid(which='major', axis='x', linewidth=0.75, color='k', alpha=0.1)
ax.grid(which='major', axis='y', linewidth=0.75, color='k', alpha=0.1)
ax.set_aspect('equal')

cycle = polygon + [polygon[0]]
# ax.plot([c.x for c in cycle], [c.y for c in cycle], 'k-')


def plot_quad(quad, ax):
    """ Plot a quad """
    points = [quad.bottom_left, quad.bottom_right,
              quad.top_right, quad.top_left, quad.bottom_left]
    # plot filled in polygon
    xs = [p.x for p in points]
    ys = [p.y for p in points]
    ax.fill(xs, ys, alpha=0.5)
    # also plot the edges with points
    ax.plot(xs, ys, 'k-', linewidth=0.5)


quads = partition(polygon)
# print('quads', quads)
for quad in quads:
    # print('plotting quad', quad)
    plot_quad(quad, ax)
