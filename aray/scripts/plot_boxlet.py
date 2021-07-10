#!/usr/bin/env python
# boxlet.py - Boxlet class and utilities

# %%
import matplotlib.pyplot as plt
import random
from math import floor, ceil
from collections import namedtuple, defaultdict
from dataclasses import dataclass
from typing import List, Optional, Tuple, Union
from itertools import product

from aray.types import Point, Quad
from aray.boxlet import Boxlet
from aray.problem import Problem


def ccw(A, B, C):
    return (C.y-A.y) * (B.x-A.x) > (B.y-A.y) * (C.x-A.x)


def check_intersection(A: Point, B: Point, C: Point, D: Point) -> bool:
    """ Check if there is an intersection between line segments AB and CD """
    if A == C or A == D or B == C or B == D:
        return False
    return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)


fig, axes = plt.subplots(2, 2)
for ax in axes.flat:
    #  generate random 2d points within [0, 10]
    while True:
        polygon = [Point(random.uniform(0, 10), random.uniform(0, 10))
                for _ in range(4)]
        cycle = polygon + [polygon[0]]
        edges = [(cycle[i], cycle[i + 1]) for i in range(len(cycle) - 1)]
        simple = not any(check_intersection(e1[0], e1[1], e2[0], e2[1])
                         for e1, e2 in product(edges, edges))
        if simple:
            break

    print('polygon=', polygon)

    ax.set_xlim(-1, 11)
    ax.set_ylim(-1, 11)
    ax.set_xticks(range(11))
    ax.set_yticks(range(11))
    ax.grid(which='major', axis='x', linewidth=0.75, color='k', alpha=0.1)
    ax.grid(which='major', axis='y', linewidth=0.75, color='k', alpha=0.1)
    ax.set_aspect('equal')

    ax.plot([c.x for c in cycle], [c.y for c in cycle], 'k-', linewidth=1)

    if simple:
        boxlets = Boxlet.from_polygon(polygon)
        print('boxlets', boxlets)
        for boxlet in boxlets:
            print('plotting boxlet', boxlet)
            points = list(boxlet.iter_points())
            xs = [p.x for p in points]
            ys = [p.y for p in points]
            assert xs, f'no points {boxlet}'
            assert ys, f'no points {boxlet}'
            print('xs', xs, 'ys', ys)
            ax.scatter(xs, ys, s=8)
plt.show()

# %%

#  generate random 2d points within [0, 10]
number = random.randint(1,79)
polygon = Problem.get(number).hole
cycle = polygon + [polygon[0]]

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


ax.plot([c.x for c in cycle], [c.y for c in cycle], 'k-', linewidth=1)

if simple:
    boxlets = Boxlet.from_polygon(polygon)
    print('boxlets', boxlets)
    for boxlet in boxlets:
        print('plotting boxlet', boxlet)
        points = list(boxlet.iter_points())
        xs = [p.x for p in points]
        ys = [p.y for p in points]
        assert xs, f'no points {boxlet}'
        assert ys, f'no points {boxlet}'
        print('xs', xs, 'ys', ys)
        ax.scatter(xs, ys, s=8)
plt.show()
