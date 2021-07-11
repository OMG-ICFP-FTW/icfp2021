#!/usr/bin/env python3

# %%
from math import sin, cos
from typing import List

from aray.util import ceil, floor
from aray.types import Point
from aray.stretch import stretch


# %%
import random
center = Point(random.uniform(3, 7), random.uniform(3, 7))
inner, outer = sorted((random.uniform(1, 6), random.uniform(1, 10)))
assert inner <= outer

import numpy as np
import matplotlib.pyplot as plt

xs = np.linspace(0, 10, 10000)
outer_upper_ys = np.sqrt(outer**2 - (xs - center.x)**2) + center.y
outer_lower_ys = -np.sqrt(outer**2 - (xs - center.x)**2) + center.y
inner_upper_ys = np.sqrt(inner**2 - (xs - center.x)**2) + center.y
inner_lower_ys = -np.sqrt(inner**2 - (xs - center.x)**2) + center.y

# plot the circles and the center
fig, ax = plt.subplots()

ax.set_xlim(-1, 11)
ax.set_ylim(-1, 11)
ax.set_xticks(range(11))
ax.set_yticks(range(11))
ax.grid(which='major', axis='x', linewidth=0.75, color='k', alpha=0.1)
ax.grid(which='major', axis='y', linewidth=0.75, color='k', alpha=0.1)
ax.set_aspect('equal')

ax.plot(xs, outer_upper_ys, 'b-')
ax.plot(xs, outer_lower_ys, 'b-')
ax.plot(xs, inner_upper_ys, 'r-')
ax.plot(xs, inner_lower_ys, 'r-')
ax.plot([center.x], [center.y], 'gx')

points = stretch(center, outer, inner)
ax.scatter([p.x for p in points], [p.y for p in points])


# %%
import random
center = Point(random.randint(3, 7), random.randint(3, 7))
inner, outer = sorted((random.randint(1, 6), random.randint(1, 10)))
assert inner <= outer

import numpy as np
import matplotlib.pyplot as plt

xs = np.linspace(0, 10, 10000)
outer_upper_ys = np.sqrt(outer**2 - (xs - center.x)**2) + center.y
outer_lower_ys = -np.sqrt(outer**2 - (xs - center.x)**2) + center.y
inner_upper_ys = np.sqrt(inner**2 - (xs - center.x)**2) + center.y
inner_lower_ys = -np.sqrt(inner**2 - (xs - center.x)**2) + center.y

# plot the circles and the center
fig, ax = plt.subplots()

ax.set_xlim(-1, 11)
ax.set_ylim(-1, 11)
ax.set_xticks(range(11))
ax.set_yticks(range(11))
ax.grid(which='major', axis='x', linewidth=0.75, color='k', alpha=0.1)
ax.grid(which='major', axis='y', linewidth=0.75, color='k', alpha=0.1)
ax.set_aspect('equal')

ax.plot(xs, outer_upper_ys, 'b-')
ax.plot(xs, outer_lower_ys, 'b-')
ax.plot(xs, inner_upper_ys, 'r-')
ax.plot(xs, inner_lower_ys, 'r-')
ax.plot([center.x], [center.y], 'gx')

points = stretch(center, outer, inner)
ax.scatter([p.x for p in points], [p.y for p in points])