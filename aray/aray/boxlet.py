#!/usr/bin/env python
# boxlet.py - Boxlet class and utilities

# %%
import matplotlib.pyplot as plt
import random
from math import floor, ceil
from collections import namedtuple, defaultdict
from dataclasses import dataclass
from typing import List, Optional, Tuple, Union

Point = namedtuple('Point', ['x', 'y'])
BoundingBox = namedtuple('BoundingBox', ['xmin', 'xmax', 'ymin', 'ymax'])

# %%


@dataclass
class Boxlet:
    """
    Boxlet class.
    """
    bound: Optional[BoundingBox]  # If none, we are empty
    top: List[int]
    bottom: List[int]

    @classmethod
    def partition(cls, points: List[Point]):
        """ Partition a simple polygon into boxlets """
        boxlets = []  # list we will fill with boxlets and return
        xs = sorted(set(p.x for p in points))
        # Adjust all of our x values by a tiny amount
        # the first point goes left, and all other points go right
        xs = [x + 1e-8 if i else x - 1e-8 for i, x in enumerate(xs)]
        xy = defaultdict(set)  # map from x -> set of y values
        for p in points:
            xy[p.x].add(p.y)
        # convert xy to map from x -> sorted list of y values
        xy = {x: sorted(ys) for x, ys in xy.items()}
        for i in range(len(xs) - 1):
            left, right = xs[i], xs[i + 1]
            ys = sorted(zip(xy[left], xy[right]))
            # Create a boxlet for each pair of ys in order
            assert len(ys) % 2 == 0, f'odd number of y values, {points}'
            for j in range(0, len(ys) - 1, 2):
                boxlet = cls.from_quad(left, right, *ys[j], *ys[j + 1])
                boxlets.append(boxlet)
        return boxlets

    @classmethod
    def from_quad(cls, left: float, right: float, top_left: float, top_right: float, bottom_left: float, bottom_right: float):
        """ Construct a quadrilateral boxlet from bounding points """
        assert left <= right, f'{left} {right}'
        assert bottom_left <= top_left, f'{bottom_left} {top_left}'
        assert bottom_right <= top_right, f'{bottom_right} {top_right}'
        # get integer x values, inside of the domain
        xmin, xmax = ceil(left), floor(right)
        ymin, ymax = ceil(min(bottom_left, bottom_right)
                          ), floor(max(top_left, top_right))

        # calculate the top
        C = (top_right - top_left) / (right - left)
        top = [floor(top_left + (x - left) * C) for x in range(xmin, xmax + 1)]
        print('C', C, 'top', top)

        # calculate the bottom
        C = (bottom_right - bottom_left) / (right - left)
        bottom = [ceil(bottom_left + (x - left) * C)
                  for x in range(xmin, xmax + 1)]
        print('C', C, 'bottom', bottom)

        if xmin <= xmax and ymin <= ymax:
            assert len(top) >= 0 and len(bottom) >= 0, f'{top} {bottom}'
            bound = BoundingBox(xmin, xmax, ymin, ymax)
        else:
            assert len(top) == 0 and len(bottom) == 0, f'{top} {bottom}'
            bound = None

        return cls(bound, top, bottom)

    @classmethod
    def from_perimeter(cls, left: int, right: int, top: List[int], bottom: List[int]):
        """ Construct a boxlet from top and bottom lists """
        assert len(top) == len(bottom), f'{top} {bottom}'
        assert left <= right, f'{left} {right}'
        assert all(t >= b for t, b in zip(top, bottom)), f'{top} {bottom}'
        bound = BoundingBox(left, right, min(bottom), max(top))
        return cls(bound, top, bottom)

    def iter_points(self):
        """ Generate all of the interior points """
        if self.bound is not None:
            for i, x in enumerate(range(self.bound.xmin, self.bound.xmax + 1)):
                for y in range(self.bottom[i], self.top[i] + 1):
                    yield Point(x, y)
        return


# %%

# generate 4 random 2d points within [0, 10]
left, right = sorted(random.uniform(0, 10) for _ in range(2))
print('left', left, 'right', right)
bottom_left, top_left = sorted(random.uniform(0, 10) for _ in range(2))
print('bottom_left', bottom_left, 'top_left', top_left)
bottom_right, top_right = sorted(random.uniform(0, 10) for _ in range(2))
print('bottom_right', bottom_right, 'top_right', top_right)
boxlet = Boxlet.from_quad(left=left, right=right, top_left=top_left,
                          top_right=top_right, bottom_left=bottom_left, bottom_right=bottom_right)
print('boxlet', boxlet)
points = list(boxlet.iter_points())
xs = [p.x for p in points]
ys = [p.y for p in points]

fig, ax = plt.subplots()
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)

# show integer grid lines
ax.set_xticks(range(11))
ax.set_yticks(range(11))
ax.grid(which='major', axis='x', linewidth=0.75, color='k', alpha=0.1)
ax.grid(which='major', axis='y', linewidth=0.75, color='k', alpha=0.1)

ax.plot([left, left, right, right, left], [bottom_left,
        top_left, top_right, bottom_right, bottom_left], 'k:')
print(f'xs({len(xs)})', xs)
print(f'ys({len(ys)})', ys)
if xs and ys:
    plt.scatter(xs, ys, color='r')
