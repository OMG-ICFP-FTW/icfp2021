#!/usr/bin/env python
# intersect.py - line intersection

# %%
import matplotlib.pyplot as plt
import random
from math import floor, ceil
from collections import namedtuple, defaultdict
from dataclasses import dataclass
from typing import List, Optional, Tuple, Union

from aray.types import Point


def intersection(A: Point, B: Point, x: float) -> Point:
    """ Get the y coordinate which corresponds to x on line AB """
    assert A.x != B.x, f'{A}, {B}, {x}'
    m = (B.y - A.y) / (B.x - A.x)
    return Point(x, A.y + m * (x - A.x))


def maybe_intersection(A: Point, B: Point, x: float) -> Optional[Point]:
    """ Get intersection if it lies on AB else None """
    if A.x <= x <= B.x or B.x <= x <= A.x:
        return intersection(A, B, x)
    return None


def intersections(A: Point, B: Point) -> List[Point]:
    """ Get all the x-lattice intersections to segment AB """
    assert A.x != B.x, f'{A}, {B}'
    left = ceil(min(A.x, B.x))
    right = floor(max(A.x, B.x))
    m = (B.y - A.y) / (B.x - A.x)
    return [Point(x, A.y + m * (x - A.x)) for x in range(left, right + 1)]
