#!/usr/bin/env python

# %%
import matplotlib.pyplot as plt
import random
from math import floor, ceil
from collections import namedtuple, defaultdict
from dataclasses import dataclass
from typing import List, Optional, Tuple, Union

from aray.types import Point
from aray.intersect import intersection, intersections, maybe_intersection

import random
N = 4
A = Point(random.uniform(0, N), random.uniform(0, N))
B = Point(random.uniform(0, N), random.uniform(0, N))
x = random.uniform(0, N)

fig, ax = plt.subplots()
ax.set_xlim(-1, N + 1)
ax.set_ylim(-1, N + 1)
ax.set_xticks(range(N + 1))
ax.set_yticks(range(N + 1))
ax.grid(which='major', axis='x', linewidth=0.75, color='k', alpha=0.1)
ax.grid(which='major', axis='y', linewidth=0.75, color='k', alpha=0.1)
ax.set_aspect('equal')

# Plot AB with points on the ends
ax.plot([A.x, B.x], [A.y, B.y], 'ko:')
# plot x as a vertical line
ax.plot([x, x], [0, N], 'r', linewidth=1)
# Plot intersections
points = intersections(A, B)
print('points', points)
ax.scatter([p.x for p in points], [p.y for p in points], color='g')
# Plot intersection
p = intersection(A, B, x)
ax.scatter([p.x], [p.y], color='b')
# Plot intersection
p = maybe_intersection(A, B, x)
if p:
    ax.scatter([p.x], [p.y], color='c')


# %%
A = Point(random.uniform(0, N), random.uniform(0, N))
B = Point(random.uniform(0, N), random.uniform(0, N))
assert intersection(A, B, A.x) == A
assert intersection(A, B, B.x) == B