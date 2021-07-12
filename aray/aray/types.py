#!/usr/bin/env python3
# types.py - utility types

import json
import os
from collections import namedtuple
from dataclasses import dataclass, fields
from typing import List, NamedTuple


class Point(NamedTuple):
    x: int
    y: int


class Pair(NamedTuple):
    a: Point
    b: Point


class Quad(NamedTuple):
    bottom_left: Point
    bottom_right: Point
    top_right: Point
    top_left: Point


# TODO: get rid of this one
Edge = namedtuple('Edge', ['a', 'b'])
