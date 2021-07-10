#!/usr/bin/env python3
# test_problem.py

import unittest
from dataclasses import asdict
from aray.boxlet import Boxlet, Point, BoundingBox


class TestBoxlet(unittest.TestCase):
    def test_simple(self):
        left = 6
        right = 7
        top = [9, 5]
        bottom = [6, 4]
        boxlet = Boxlet.from_perimeter(
            left=left, right=right, top=top, bottom=bottom)
        xs = [6, 6, 6, 6, 7, 7]
        ys = [6, 7, 8, 9, 4, 5]
        points = list(zip(xs, ys))
        self.assertEqual(list(boxlet.iter_points()), points)



if __name__ == '__main__':
    unittest.main()
