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
Quad = namedtuple(
    'Quad', ['bottom_left', 'bottom_right', 'top_right', 'top_left'])

# %%


@dataclass
class Boxlet:
    xmin: int
    xmax: int
    ymin: int
    ymax: int
    top: List[int]  # should be length xmax - xmin + 1
    bottom: List[int]  # same length as top

    @classmethod
    def partition(cls, points: List[Point]):
        """ Partition a simple polygon into boxlets """
        boxlets = []  # list we will fill with boxlets and return
        xs = sorted(set(p.x for p in points))
        xy = defaultdict(list)  # map from x -> list of y values
        for p in points:
            # add p.y twice, once for each line segment
            xy[p.x].append(p.y)
            xy[p.x].append(p.y)
        # convert xy to map from x -> sorted list of y values
        xy = {x: sorted(ys) for x, ys in xy.items()}
        for x in xs:
            print('xy', x, xy[x])
        exclude = None
        for i in range(len(xs) - 1):
            left, right = ceil(xs[i]), floor(xs[i + 1])
            if left == exclude:
                left += 1  # avoid double-counting columns
            exclude = right  # set new bound for next iteration
            if right < left:  # doesn't cover any integer points
                continue
            ys = list(reversed(sorted(zip(xy[xs[i]], xy[xs[i + 1]]))))
            print('ys', ys)
            # Create a boxlet for each pair of ys in order
            assert len(ys) % 2 == 0, f'odd number of y values, {points}'
            for j in range(0, len(ys) - 1, 2):
                quad = Quad(bottom_left=Point(xs[i], ys[j + 1][0]),
                            bottom_right=Point(xs[i + 1], ys[j + 1][1]),
                            top_right=Point(xs[i + 1], ys[j][1]),
                            top_left=Point(xs[i], ys[j][0]))
                assert quad.top_left.y >= quad.bottom_left.y, f'{quad}'
                assert quad.top_right.y >= quad.bottom_right.y, f'{quad}'
                assert quad.top_left.x <= quad.top_right.x, f'{quad}'
                assert quad.bottom_left.x <= quad.bottom_right.x, f'{quad}'
                boxlet = cls.from_quad(left, right, quad)
                boxlets.append(boxlet)
        return boxlets

    @classmethod
    def from_quad(cls, left: int, right: int, quad: Quad):
        """ Construct a quadrilateral boxlet from bounding points """
        assert left <= right, f'{left} {right}'
        assert quad.top_left.y >= quad.bottom_left.y, f'{quad}'
        assert quad.top_right.y >= quad.bottom_right.y, f'{quad}'
        assert quad.top_left.x <= quad.top_right.x, f'{quad}'
        assert quad.bottom_left.x <= quad.bottom_right.x, f'{quad}'
        # Only deal with column quads for now
        assert quad.top_left.x == quad.bottom_left.x, f'{quad}'
        assert quad.top_right.x == quad.bottom_right.x, f'{quad}'

        if quad.top_left.x == quad.top_right.x: # Single column
            top = [quad.top_left.y]
            bottom = [quad.bottom_left.y]
        else:  # linear interpolation
            # calculate the top
            C = (quad.top_right.y - quad.top_left.y) / \
                (quad.top_right.x - quad.top_left.x)
            top = [quad.top_left.y + (x - quad.top_left.x)
                * C for x in range(left, right + 1)]
            top = [floor(y) for y in top]
            # calculate the bottom
            C = (quad.bottom_right.y - quad.bottom_left.y) / \
                (quad.bottom_right.x - quad.bottom_left.x)
            bottom = [quad.bottom_left.y +
                    (x - quad.bottom_left.x) * C for x in range(left, right + 1)]
            bottom = [ceil(y) for y in bottom]

        xmin = left
        xmax = right
        ymin = min(bottom)
        ymax = max(top)
        return cls(xmin, xmax, ymin, ymax, top, bottom)

    @classmethod
    def from_perimeter(cls, left: int, right: int, top: List[int], bottom: List[int]):
        """ Construct a boxlet from top and bottom lists """
        assert len(top) == len(bottom), f'{top} {bottom}'
        assert left <= right, f'{left} {right}'
        assert all(t >= b for t, b in zip(top, bottom)), f'{top} {bottom}'
        raise NotImplementedError

    def iter_points(self):
        """ Generate all of the interior points """
        for i, x in enumerate(range(self.xmin, self.xmax + 1)):
            for y in range(self.bottom[i], self.top[i] + 1):
                yield Point(x, y)
        return

# %%  generate 3 random 2d points within [0, 10]
polygon = [Point(random.uniform(0, 10), random.uniform(0, 10))
           for _ in range(3)]

fig, ax = plt.subplots()
ax.set_xlim(-1, 11)
ax.set_ylim(-1, 11)
ax.set_xticks(range(11))
ax.set_yticks(range(11))
ax.grid(which='major', axis='x', linewidth=0.75, color='k', alpha=0.1)
ax.grid(which='major', axis='y', linewidth=0.75, color='k', alpha=0.1)
ax.set_aspect('equal')

cycle = polygon + [polygon[0]]
ax.plot([c.x for c in cycle], [c.y for c in cycle], 'k:')
plt.show()

boxlets = Boxlet.partition(polygon)
print('boxlets', boxlets)

# %%
points = list(boxlet.iter_points())
xs = [p.x for p in points]
ys = [p.y for p in points]

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
    plt.scatter(xs, ys)


# %%
for fname in ['uniform', 'randint']:
    fig, axes = plt.subplots(2, 2)
    fig.suptitle(fname)
    fn = getattr(random, fname)
    for ax in axes.flat:
        bottom_left_y, top_left_y = sorted(fn(0, 10) for _ in range(2))
        bottom_right_y, top_right_y = sorted(fn(0, 10) for _ in range(2))
        left_x, right_x = sorted(fn(0, 10) for _ in range(2))
        print('top left y', top_left_y, 'bottom left y', bottom_left_y)
        print('top right y', top_right_y, 'bottom right y', bottom_right_y)
        print('left x', left_x, 'right x', right_x)
        quad = Quad(top_left=Point(left_x, top_left_y),
                    top_right=Point(right_x, top_right_y),
                    bottom_right=Point(right_x, bottom_right_y),
                    bottom_left=Point(left_x, bottom_left_y))
        left = ceil(left_x)
        right = floor(right_x)

        ax.set_xlim(-1, 11)
        ax.set_ylim(-1, 11)
        ax.set_xticks(range(11))
        ax.set_yticks(range(11))
        ax.grid(which='major', axis='x', linewidth=0.75, color='k', alpha=0.1)
        ax.grid(which='major', axis='y', linewidth=0.75, color='k', alpha=0.1)
        # plot quad
        points = [quad.bottom_left, quad.bottom_right,
                  quad.top_right, quad.top_left, quad.bottom_left]
        ax.plot([p.x for p in points], [p.y for p in points], 'k:')
        # plot boxlet, if nonzero interior points
        if left <= right:
            boxlet = Boxlet.from_quad(left, right, quad)
            print('boxlet', boxlet)
            points = list(boxlet.iter_points())
            xs = [p.x for p in points]
            ys = [p.y for p in points]
            assert xs, f'no points {left} {right}, {quad}'
            assert ys, f'no points {left} {right}, {quad}'
            ax.scatter(xs, ys, s=4)
