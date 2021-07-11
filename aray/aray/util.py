#!/usr/bin/env python3
# util.py - utility functions

import math

from .types import Point

MACHINE_EPS = 1e-9


def dist(a: Point, b: Point):
    """Return the squared distance between two points"""
    return (a.x - b.x) ** 2 + (a.y - b.y) ** 2


def ceil(x):
    """Return the ceiling of x as a float, but fudge it by epsilon"""
    # if x is within MACHINE_EPS of an integer, return that integer
    if abs(x - round(x)) < MACHINE_EPS:
        return round(x)
    # otherwise, return the ceiling of x
    return math.ceil(x)


def floor(x):
    """Return the floor of x as a float, but fudge it by epsilon"""
    # if x is within MACHINE_EPS of an integer, return that integer
    if abs(x - round(x)) < MACHINE_EPS:
        return round(x)
    # otherwise, return the floor of x
    return math.floor(x)