#!/usr/bin/env python3
# stretch.py - get lattice points within a donut circle shape

# %%
from math import sin, cos
from typing import List

from .util import ceil, floor
from .types import Point


def stretch(start: Point, d_old: int, epsilon: int) -> List[Point]:
    """ Get the valid set of points for a given start and old squared distance """
    outer = (1 + epsilon / 1e6) * (d_old ** 0.5)
    inner = (1 - epsilon / 1e6) * (d_old ** 0.5)
    x_outer_min = ceil(start.x - outer)
    x_outer_max = floor(start.x + outer)
    x_inner_min = floor(start.x - inner)
    x_inner_max = ceil(start.x + inner)
    points = []
    for x in range(x_outer_min, x_outer_max + 1):
        delta_x = abs(x - start.x)
        if x <= x_inner_min or x >= x_inner_max:
            assert delta_x > inner
            # calculate the y values on outer circle for this x
            delta_y = (outer ** 2 - delta_x ** 2) ** 0.5
            y_outer_max = floor(start.y + delta_y)
            y_outer_min = ceil(start.y - delta_y)
            for y in range(y_outer_min, y_outer_max + 1):
                points.append(Point(x, y))
        else:
            assert delta_x <= inner, f'{delta_x} {inner}'
            # only calculate the y values between outer and inner circles
            delta_y_outer = abs(outer ** 2 - delta_x ** 2) ** 0.5
            delta_y_inner = abs(inner ** 2 - delta_x ** 2) ** 0.5
            y_outer_max = floor(start.y + delta_y_outer)
            y_outer_min = ceil(start.y - delta_y_outer)
            y_inner_max = ceil(start.y + delta_y_inner)
            y_inner_min = floor(start.y - delta_y_inner)
            for y in range(y_outer_min, y_inner_min + 1):
                points.append(Point(x, y))
            for y in range(y_inner_max, y_outer_max + 1):
                points.append(Point(x, y))
    return points
