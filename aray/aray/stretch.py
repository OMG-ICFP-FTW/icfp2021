#!/usr/bin/env python3
# stretch.py - get lattice points within a donut circle shape

# %%
from math import sin, cos
from typing import List, Set

from .util import ceil, floor, dist
from .types import Point


def slow_stretch(a: Point, b: Point, epsilon: int) -> List[Point]:
    """ Get the valid set of deltas for a given old squared distance """
    # Deltas are just points centred on the origin
    d = dist(a, b)
    n = ceil(d ** .5 + 1)
    center = Point(0, 0)
    points = []
    for x in range(-n, n + 1):
        for y in range(-n, n + 1):
            p = Point(x, y)
            if abs(dist(center, Point(x, y))/d - 1) <= epsilon / 1_000_000:
                points.append(Point(x, y))
    return points


def stretch(start: Point, d_old: int, epsilon: int, placement: Set[Point]) -> Set[Point]:
    """ Get the valid set of points for a given start and old squared distance """
    outer = (1 + epsilon / 1e6) * (d_old ** 0.5)
    inner = (1 - epsilon / 1e6) * (d_old ** 0.5)
    x_outer_min = ceil(start.x - outer)
    x_outer_max = floor(start.x + outer)
    x_inner_min = floor(start.x - inner)
    x_inner_max = ceil(start.x + inner)
    points = set()
    for point in placement:
        x = point.x
        if x < x_outer_min or x > x_outer_max:  # out of outer circle
            continue
        delta_x = abs(x - start.x)
        y = point.y
        if x <= x_inner_min or x >= x_inner_max:
            assert delta_x >= inner, f'{delta_x} {inner} {x} {x_inner_min} {x_inner_max}'
            # calculate the y values on outer circle for this x
            delta_y = (outer ** 2 - delta_x ** 2) ** 0.5
            y_outer_max = floor(start.y + delta_y)
            y_outer_min = ceil(start.y - delta_y)
            if y_outer_min <= y <= y_outer_max:
                points.add(point)
        else:
            assert delta_x <= inner, f'{delta_x} {inner}'
            # only calculate the y values between outer and inner circles
            delta_y_outer = abs(outer ** 2 - delta_x ** 2) ** 0.5
            delta_y_inner = abs(inner ** 2 - delta_x ** 2) ** 0.5
            y_outer_max = floor(start.y + delta_y_outer)
            y_outer_min = ceil(start.y - delta_y_outer)
            y_inner_max = ceil(start.y + delta_y_inner)
            y_inner_min = floor(start.y - delta_y_inner)
            if y_outer_min <= y <= y_inner_min:
                points.add(point)
            elif y_inner_max <= y <= y_outer_max:
                points.add(point)
    return points



def old_stretch(start: Point, d_old: int, epsilon: int) -> List[Point]:
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
            assert delta_x >= inner, f'{delta_x} {inner} {x} {x_inner_min} {x_inner_max}'
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


def delta_stretch(a: Point, b: Point, epsilon: int) -> List[Point]:
    """ Get the valid set of deltas for a given old squared distance """
    # Deltas are just points centred on the origin
    d_old = (a.x - b.x) ** 2 + (a.y - b.y) ** 2
    return old_stretch(Point(0, 0), d_old, epsilon)


def center_stretch(d_old: int, epsilon: int) -> List[Point]:
    return old_stretch(Point(0, 0), d_old, epsilon)