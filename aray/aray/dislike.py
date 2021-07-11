#!/usr/bin/env python3
# dislike.py - scoring function for solutions

from typing import List

from .types import Point
from .util import dist


def dislikes(hole: List[Point], points: List[Point]) -> int:
    """Calculates the minimum distance to a vertex in positions for each vertex in the hole."""
    return sum(min([dist(h, v) for v in points]) for h in hole)
