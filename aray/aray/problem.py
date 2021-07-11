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


# Path of 'icfp2021' directory
BASE_PATH = base = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.realpath(__file__))))


@dataclass
class Problem:
    hole: List[Point]
    vertices: List[Point]
    edges: List[Edge]
    epsilon: int

    @classmethod
    def get(cls, number):
        filename = os.path.join(BASE_PATH, 'problems', f'{number}.json')
        with open(filename, 'r') as f:
            data = json.load(f)
        hole = [Point(x, y) for x, y in data['hole']]
        vertices = [Point(x, y) for x, y in data['figure']['vertices']]
        edges = [Edge(a, b) for a, b in data['figure']['edges']]
        epsilon = int(data['epsilon'])
        return cls(hole, vertices, edges, epsilon)

    def json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


@dataclass
class Pose:
    vertices: List[Point]

    @classmethod
    def from_json(cls, data):
        assert isinstance(data, dict), f'{data} is not a dict'
        assert tuple(data.keys()) == ('vertices',), f'{data} is not a pose'
        vertices = [Point(x, y) for x, y in data['vertices']]
        return cls(vertices)

    def json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
