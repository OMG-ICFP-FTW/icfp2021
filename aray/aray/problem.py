#!/usr/bin/env python3
# problem.py - dataclass for problem definition

# %%
import os
import json
from dataclasses import dataclass, fields
from typing import List
from collections import namedtuple

Point = namedtuple('Point', ['x', 'y'])
Edge = namedtuple('Edge', ['a', 'b'])

def dataclass_from_dict(cls, d):
    """ Recursive dataclass builder """
    try:
        fieldtypes = {f.name:f.type for f in fields(cls)}
        return cls(**{f:dataclass_from_dict(fieldtypes[f],d[f]) for f in d})
    except:
        return d # Not a dataclass field


# Path of 'icfp2021' directory
BASE_PATH = base = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.realpath(__file__))))


@dataclass
class Figure:
    vertices: List[Point]
    edges: List[Edge]


@dataclass
class Problem:
    hole: List[Point]
    figure: Figure
    epsilon: int

    @classmethod
    def get(cls, number):
        filename = os.path.join(BASE_PATH, 'problems', f'{number}.json')
        with open(filename, 'r') as f:
            return dataclass_from_dict(cls, json.load(f))


    def json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


@dataclass
class Pose:
    vertices: List[Point]

    def json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
