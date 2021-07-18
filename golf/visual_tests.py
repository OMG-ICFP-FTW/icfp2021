#!/usr/bin/env python3
# visual_tests.py - Visually test some of the solver multiplication


'''
Cases to test:

The hole points are H1, H2, forming line segment HH
The edge points are A, B, forming line segment AB

Test AB HH are identical

Test AB HH are collinear and disjoint
Test AB HH are collinear and touching
Test AB HH are collinear and intersect

Test AB HH are parallel

Test AB HH are intersecting but do not overlap
Test AB HH are intersecting and overlap at an end (like a L)
Test AB HH are intersecting and overlap at a point (like a T)
Test AB HH are intersecting and overlap in the center (like a X)

Whole hole tests
H1, H2, H3 form a triangle
Test AB inside the triangle
Test AB along each of the edges
Test AB crosses from inside to outside
Test AB starts at point and goes inside
Test AB starts at point and goes outside
Test AB starts at midpoint and goes outside

Concave hole tests
Hole forms a U shape
Test AB inside the hole
Test AB along each of the edges
Test AB along the top of the U, point to point
Test AB across the middle of the U, midpoint to midpoint
Test AB across the U from midpoint to point, diagonally
Test AB across the U from point to midpoint, diagonally
Test AB from inside the U across to the opposite midpoint
Test AB from inside the U across to the opposite point

J shaped hole
    ..
..  ..
..  ..
......

Test that AB from far top point across to 

'''
# %%
from typing import List
from dataclasses import dataclass
from itertools import product
from collections import namedtuple
import matplotlib.pyplot as plt

from andtools import Problem

# %%
# https://www.geeksforgeeks.org/check-if-two-given-line-segments-intersect/
Coord = namedtuple('Coord', ['x', 'y'])


def onSegment(p: Coord, q: Coord, r: Coord) -> bool:
    ''' Return True if point q lies on line segment 'pr' '''
    return (q.x <= max(p.x, r.x) and q.x >= min(p.x, r.x) and
            q.y <= max(p.y, r.y) and q.y >= min(p.y, r.y))


def orient(p: Coord, q: Coord, r: Coord):
    ''' Get orientation of triangle pqr (Collinear, Clockwise, Counterclockwise) '''
    val = (q.y - p.y) * (r.x - q.x) - (q.x - p.x) * (r.y - q.y)
    return 0 if val == 0 else (1 if val > 0 else 2)


'''// The main function that returns true if line segment 'p1q1'
// and 'p2q2' intersect.
bool doIntersect(Point p1, Point q1, Point p2, Point q2)
{
    // Find the four orientations needed for general and
    // special cases
    int o1 = orientation(p1, q1, p2);
    int o2 = orientation(p1, q1, q2);
    int o3 = orientation(p2, q2, p1);
    int o4 = orientation(p2, q2, q1);
  
    // General case
    if (o1 != o2 && o3 != o4)
        return true;
  
    // Special Cases
    // p1, q1 and p2 are colinear and p2 lies on segment p1q1
    if (o1 == 0 && onSegment(p1, p2, q1)) return true;
  
    // p1, q1 and q2 are colinear and q2 lies on segment p1q1
    if (o2 == 0 && onSegment(p1, q2, q1)) return true;
  
    // p2, q2 and p1 are colinear and p1 lies on segment p2q2
    if (o3 == 0 && onSegment(p2, p1, q2)) return true;
  
     // p2, q2 and q1 are colinear and q1 lies on segment p2q2
    if (o4 == 0 && onSegment(p2, q1, q2)) return true;
  
    return false; // Doesn't fall in any of the above cases
}
'''
def intersecting(p1: Coord, q1: Coord, p2: Coord, q2: Coord) -> bool:
    ''' Return True if line segments p1q1 and p2q2 intersect '''
    o1 = orient(p1, q1, p2)
    o2 = orient(p1, q1, q2)
    o3 = orient(p2, q2, p1)
    o4 = orient(p2, q2, q1)

    # General case
    if o1 != o2 and o3 != o4:
        return True

    # Special Cases
    # p1, q1 and p2 are colinear and p2 lies on segment p1q1
    if o1 == 0 and onSegment(p1, p2, q1):
        return True
    # p1, q1 and q2 are colinear and q2 lies on segment p1q1
    if o2 == 0 and onSegment(p1, q2, q1):
        return True
    # p2, q2 and p1 are colinear and p1 lies on segment p2q2
    if o3 == 0 and onSegment(p2, p1, q2):
        return True
    # p2, q2 and q1 are colinear and q1 lies on segment p2q2
    if o4 == 0 and onSegment(p2, q1, q2):
        return True

    return False  # Doesn't fall in any of the above cases


def valid(a: Coord, b: Coord, c: Coord, d: Coord) -> bool:
    ''' Return True if segments a-b and hole c-d are valid in combination '''
    if (a == c and b == d) or (a == d and b == c):
        return True
    o1 = orient(a, b, c)
    o2 = orient(a, b, d)
    o3 = orient(c, d, a)
    o4 = orient(c, d, b)

    # General case
    if o1 != o2 and o3 != o4:
        return False
    
    # Special Cases

    if o1 == 0 or o2 == 0 or o3 == 0 or o4 == 0:
        return False
    return (o1 != o2 and o3 != o4)  # crossing intersection or not


@dataclass
class TestCase:
    name: str
    a: Coord
    b: Coord
    hole: List[Coord]
    expected: bool

    def valid(self):
        is_valid = True
        for i in range(len(self.hole) - 1):
            if not intersecting(self.a, self.b, self.hole[i], self.hole[i + 1]):
                is_valid = False
                break
        return is_valid

    def plot(self):
        fig, ax = plt.subplots(figsize=(2,2))
        for i in range(len(self.hole)):
            h1, h2 = self.hole[i], self.hole[(i + 1) % len(self.hole)]
            ax.plot([h1.x, h2.x], [h1.y, h2.y], 'co-', alpha=.5)
        ax.plot([self.a.x, self.b.x], [self.a.y, self.b.y], 'mo-', alpha=.5)
        # Show gridlines
        ax.grid(True)
        xmin = min(0, self.a.x, self.b.x, min(c.x for c in self.hole))
        xmax = max(1, self.a.x, self.b.x, max(c.x for c in self.hole))
        ymin = min(0, self.a.y, self.b.y, min(c.y for c in self.hole))
        ymax = max(1, self.a.y, self.b.y, max(c.y for c in self.hole))
        # Set x and y limits
        ax.set_xlim([xmin - 1, xmax + 1])
        ax.set_ylim([ymin - 1, ymax + 1])
        ax.set_xticks(range(xmin, xmax + 1))
        ax.set_yticks(range(ymin, ymax + 1))
        # set title
        ax.set_title(self.name)
        # set labels
        valid = self.valid()
        ax.set_xlabel(f'Got: {valid}')
        ax.set_ylabel(f'Expected: {self.expected}')
        if valid != self.expected:
            ax.set_facecolor((1, .7, .7))
        # Set coloring
        plt.show()

# %% Test AB HH are identical
pairs = [
    (Coord(0, 0), Coord(0, 0)),
    (Coord(0, 0), Coord(0, 1)),
    (Coord(0, 0), Coord(1, 0)),
    (Coord(0, 0), Coord(1, 1)),
    (Coord(0, 1), Coord(1, 0)),
]
for a, b in pairs:
    # TestCase(a, b, [a, b]).assert_valid()
    TestCase('identity', a, b, [a, b], True).plot()

# %% Test AB HH are collinear and disjoint
abhole = [
    (Coord(0, 0), Coord(0, 1), [Coord(0, 2), Coord(0, 3)]),
    (Coord(0, 0), Coord(1, 0), [Coord(2, 0), Coord(3, 0)]),
    (Coord(0, 0), Coord(1, 1), [Coord(2, 2), Coord(3, 3)]),
    (Coord(0, 3), Coord(1, 2), [Coord(2, 1), Coord(3, 0)]),
    (Coord(0, 2), Coord(0, 3), [Coord(0, 0), Coord(0, 1)]),
    (Coord(2, 0), Coord(3, 0), [Coord(0, 0), Coord(1, 0)]),
    (Coord(2, 2), Coord(3, 3), [Coord(0, 0), Coord(1, 1)]),
    (Coord(2, 1), Coord(3, 0), [Coord(0, 3), Coord(1, 2)]),
]
for a, b, hole in abhole:
    TestCase('collinear disjoint', a, b, hole, True).plot()

# %% Test AB HH are collinear and intersecting
abhole = [
    (Coord(0, 0), Coord(0, 2), [Coord(0, 1), Coord(0, 3)]),
    (Coord(0, 0), Coord(2, 0), [Coord(1, 0), Coord(3, 0)]),
    (Coord(0, 0), Coord(2, 2), [Coord(1, 1), Coord(3, 3)]),
    (Coord(0, 3), Coord(2, 1), [Coord(1, 2), Coord(3, 0)]),
    (Coord(0, 1), Coord(0, 3), [Coord(0, 0), Coord(0, 2)]),
    (Coord(1, 0), Coord(3, 0), [Coord(0, 0), Coord(2, 0)]),
    (Coord(1, 1), Coord(3, 3), [Coord(0, 0), Coord(2, 2)]),
    (Coord(1, 2), Coord(3, 0), [Coord(0, 3), Coord(2, 1)]),
]
for a, b, hole in abhole:
    TestCase('collinear intersect', a, b, hole, False).plot()

# %% Test AB HH are collinear and abut
abhole = [
    (Coord(0, 0), Coord(0, 2), [Coord(0, 1), Coord(0, 2)]),
    (Coord(0, 0), Coord(2, 0), [Coord(1, 0), Coord(2, 0)]),
    (Coord(0, 0), Coord(2, 2), [Coord(1, 1), Coord(2, 2)]),
    (Coord(0, 0), Coord(0, 2), [Coord(0, 1), Coord(0, 2)]),
    (Coord(0, 0), Coord(0, 2), [Coord(0, 0), Coord(0, 1)]),
    (Coord(0, 0), Coord(2, 0), [Coord(0, 0), Coord(1, 0)]),
    (Coord(0, 0), Coord(2, 2), [Coord(0, 0), Coord(1, 1)]),
    (Coord(0, 0), Coord(0, 2), [Coord(0, 0), Coord(0, 1)]),
]
for a, b, hole in abhole:
    TestCase('collinear abut', a, b, hole, True).plot()

# %% Test AB HH are collinear and overlap
abhole = [
    (Coord(0, 0), Coord(0, 3), [Coord(0, 1), Coord(0, 2)]),
    (Coord(0, 0), Coord(3, 0), [Coord(1, 0), Coord(2, 0)]),
    (Coord(0, 0), Coord(3, 3), [Coord(1, 1), Coord(2, 2)]),
    (Coord(0, 3), Coord(3, 0), [Coord(1, 2), Coord(2, 1)]),
]
for a, b, hole in abhole:
    TestCase('collinear overlap', a, b, hole, True).plot()
