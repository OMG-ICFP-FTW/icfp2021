#!/usr/bin/env python
# boxlet.py - Boxlet class and utilities

# %%
import matplotlib.pyplot as plt
import random
from collections import namedtuple, defaultdict
from dataclasses import dataclass
from typing import List, Optional, Tuple, Union

from .types import Point, Quad
from .intersect import intersections, intersection, maybe_intersection
from .util import floor, ceil

def partition(points: List[Point]):
    """ Partition a simple polygon into a list of Quads """
    quads = []  # list we will fill with quads and return
    xs = sorted(set(p.x for p in points))
    # Get all our y points for each x
    left_xy = defaultdict(list)  # map [x] -> left_ys
    right_xy = defaultdict(list)  # map [x] -> right_ys
    for x in xs:
        for i in range(len(points)):
            A = points[i]
            B = points[(i + 1) % len(points)]
            if A.x == x == B.x:
                continue
            else:
                # Switch to left and right sides
                C = min(A, B, key=lambda p: p.x)
                D = max(A, B, key=lambda p: p.x)
                if x == C.x:
                    left_xy[x].append(C.y)
                elif x == D.x:
                    right_xy[x].append(D.y)
                elif x < C.x or x > D.x:
                    continue
                else:
                    p = intersection(C, D, x)
                    left_xy[x].append(p.y)
                    right_xy[x].append(p.y)
    # Get all our quads
    exclude = None
    for i in range(len(xs) - 1):
        xmin, xmax = xs[i], xs[i + 1]
        assert xmin < xmax, f'{points}'
        left, right = ceil(xmin), floor(xmax)
        if left == exclude:
            left += 1  # avoid double-counting columns
        exclude = right  # set new bound for next iteration
        if right < left:  # doesn't cover any integer points
            continue
        # Create a quad for each pair of ys in order
        left_ys = sorted(left_xy[xmin])
        right_ys = sorted(right_xy[xmax])
        ys = list(zip(left_ys, right_ys))
        assert len(ys) % 2 == 0, f'odd number of y values, {points}\n{ys}\n{(xmin,xmax)}'
        for j in range(0, len(ys) - 1, 2):
            bottom_left = Point(xmin, ys[j][0])
            top_left = Point(xmin, ys[j + 1][0])
            bottom_right = Point(xmax, ys[j][1])
            top_right = Point(xmax, ys[j + 1][1])
            # check that we have at least 3 unique points
            assert len(set((bottom_left, top_left, bottom_right, top_right))), \
                f'{points}\n{bottom_left}\n{top_left}\n{bottom_right}\n{top_right}'

            quad = Quad(bottom_left=bottom_left, bottom_right=bottom_right,
                        top_right=top_right, top_left=top_left)
            assert quad.top_left.y >= quad.bottom_left.y, f'{quad}'
            assert quad.top_right.y >= quad.bottom_right.y, f'{quad}'
            assert quad.top_left.x <= quad.top_right.x, f'{quad}'
            assert quad.bottom_left.x <= quad.bottom_right.x, f'{quad}'
            quads.append(quad)
    return quads


