#!/usr/bin/env python
# boxlet.py - Boxlet class and utilities

# %%
import matplotlib.pyplot as plt
import random
from collections import namedtuple, defaultdict
from dataclasses import dataclass
from typing import List, Optional, Tuple, Union

from .util import floor, ceil
from .types import Point, Quad
from .intersect import intersections
from .partition import partition


@dataclass
class Boxlet:
    top: List[Point]
    bottom: List[Point]

    @classmethod
    def from_polygon(cls, points: List[Point]):
        """ Create a boxlet from a simple polygon """
        boxlets = []  # list we will fill with boxlets and return
        quads = partition(points)
        last_column = None
        for i, quad in enumerate(quads):
            left = ceil(quad.bottom_left.x)
            right = floor(quad.top_right.x)
            if last_column is not None and left == last_column:
                left += 1
            last_column = right
            boxlet = cls.from_quad(left, right, quad)
            if boxlet is not None and len(boxlet.top) > 0:
                boxlets.append(boxlet)
        return boxlets

    @classmethod
    def from_quad(cls, left: int, right: int, quad: Quad):
        """ Construct a quadrilateral boxlet from bounding points """
        assert isinstance(left, int) and isinstance(
            right, int), f'{left} {right}'
        assert left <= right, f'{left} {right}'
        assert quad.top_left.y >= quad.bottom_left.y, f'{quad}'
        assert quad.top_right.y >= quad.bottom_right.y, f'{quad}'
        assert quad.top_left.x <= quad.top_right.x, f'{quad}'
        assert quad.bottom_left.x <= quad.bottom_right.x, f'{quad}'
        # Only deal with column quads for now
        assert quad.top_left.x == quad.bottom_left.x, f'{quad}'
        assert quad.top_right.x == quad.bottom_right.x, f'{quad}'
        # Check that we have at least 3 unique points
        assert len(set(quad)) >= 3, f'{quad}\n{set(quad)}'

        if quad.top_left.x == quad.top_right.x:  # Single column
            top = [quad.top_left]
            bottom = [quad.bottom_left]
        else:  # linear interpolation
            top_points = intersections(quad.top_left, quad.top_right)
            bottom_points = intersections(quad.bottom_left, quad.bottom_right)
            assert len(top_points) == len(bottom_points), f'{quad}'
            top = []
            bottom = []
            for t, b in zip(top_points, bottom_points):
                assert t.x == b.x, f'{quad}'
                ymax = floor(t.y)
                ymin = ceil(b.y)
                if ymax < ymin:
                    continue
                else:
                    top.append(Point(t.x, ymax))
                    bottom.append(Point(t.x, ymin))
        return cls(top=top, bottom=bottom)

    def iter_points(self):
        """ Generate all of the interior points """
        for t, b in zip(self.top, self.bottom):
            assert t.x == b.x, f'{self}'
            for y in range(b.y, t.y + 1):
                yield Point(t.x, y)
