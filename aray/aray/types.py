#!/usr/bin/env python3
# types.py - utility types

import os
import json
from dataclasses import dataclass, fields
from typing import List
from collections import namedtuple

Point = namedtuple('Point', ['x', 'y'])
Edge = namedtuple('Edge', ['a', 'b'])
Quad = namedtuple(
    'Quad', ['bottom_left', 'bottom_right', 'top_right', 'top_left'])

