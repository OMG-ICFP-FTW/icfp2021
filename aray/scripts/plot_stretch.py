#!/usr/bin/env python3

# %%
from math import sin, cos
from typing import List

import numpy as np
import matplotlib.pyplot as plt

from aray.util import ceil, floor
from aray.types import Point
from aray.stretch import stretch


import random

for fname in ['uniform', 'randint']:
    fn = getattr(random, fname)
    fig, axes = plt.subplots(2, 2, figsize=(8, 8))
    for ax in axes.flat:
        center = Point(fn(3, 7), fn(3, 7))
        # print('center', center)
        r_old = fn(2, 4)
        frac = random.uniform(0.2, 0.3)
        inner = r_old * (1 - frac)
        outer = r_old * (1 + frac)
        d_old = r_old ** 2
        epsilon = int(frac * 1e6)
        assert inner <= outer
        # print('r', r_old, 'inner', inner, 'outer', outer)

        xs = np.linspace(0, 10, 10000)
        outer_upper_ys = np.sqrt(outer**2 - (xs - center.x)**2) + center.y
        outer_lower_ys = -np.sqrt(outer**2 - (xs - center.x)**2) + center.y
        inner_upper_ys = np.sqrt(inner**2 - (xs - center.x)**2) + center.y
        inner_lower_ys = -np.sqrt(inner**2 - (xs - center.x)**2) + center.y


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

        points = stretch(center, d_old, epsilon)
        # print(points)
        ax.scatter([p.x for p in points], [p.y for p in points])


        # TODO: use this for checking
        def stretch_check(center: Point, outer_radius: float, inner_radius: float) -> List[Point]:
            """ Get the set of points that are between inner_radius and outer_radius away from center """
            # Do this the simple way, where we evaluate every single point
            # and then filter out the ones that are outside the outer circle,
            # or inside the inner circle
            xmin = ceil(center.x - outer_radius)
            xmax = floor(center.x + outer_radius)
            ymin = ceil(center.y - outer_radius)
            ymax = floor(center.y + outer_radius)
            points = []
            for x in range(xmin, xmax + 1):
                for y in range(ymin, ymax + 1):
                    r = (x - center.x)**2 + (y - center.y)**2
                    if r <= outer_radius**2 and r >= inner_radius**2:
                        points.append(Point(x, y))
            return points

        check_points = stretch_check(center, outer, inner)

        # check that points are the same
        assert len(points) == len(check_points)
        assert set(points) == set(check_points), f'{set(points) - set(check_points)}'
