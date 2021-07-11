#!/usr/bin/env python3
# stretch.py - get lattice points within a donut circle shape

# %%
from math import sin, cos
from typing import List

from .util import ceil, floor
from .types import Point

# %%
def stretch(center: Point, outer_radius: float, inner_radius: float) -> List[Point]:
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
