#!/usr/bin/env python3
# problem.py - dataclass for problem definition

# %%
import os
import json
from dataclasses import dataclass
from typing import List, Set, Dict, Optional
from collections import defaultdict
import requests

from .types import Point, Edge
from .util import dist


# Path of 'icfp2021' directory
BASE_PATH = base = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.realpath(__file__))))


def get_problem_json_path(i: int) -> str:
    filename = os.path.join(BASE_PATH, 'problems', f'{i}.json')
    # if it doesn't exist, download it
    if not os.path.exists(filename):
        # first ensure the directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        # download the file
        print(f'Downloading problem {i}')
        TEAM_NAME = "OMG ICFP FTW"
        headers = {"Authorization": "Bearer " + os.environ['ICFP2021_API_KEY']}
        r = requests.get(
            f"https://poses.live/api/problems/{i}", headers=headers)
        r.raise_for_status()
        data = r.json()
        print('got data', data)
        # Write data to file
        with open(filename, 'w') as f:
            json.dump(data, f)
    return filename


@dataclass
class Problem:
    hole: List[Point]
    vertices: List[Point]  # original vertices
    edges: List[Edge]  # list of edges in the pose
    dists: List[int]  # squared distance for original edge lengths
    edge_map: Dict[int, List[int]]  # map vertex index -> list of edge indexes
    epsilon: int

    @classmethod
    def get(cls, number):
        filename = get_problem_json_path(number)
        with open(filename, 'r') as f:
            data = json.load(f)
        hole = [Point(x, y) for x, y in data['hole']]
        vertices = [Point(x, y) for x, y in data['figure']['vertices']]
        edges = [Edge(a, b) for a, b in data['figure']['edges']]
        dists = [dist(vertices[a], vertices[b]) for a, b in edges]
        edge_map = defaultdict(list)
        for i, edge in enumerate(edges):
            edge_map[edge.a].append(i)
            edge_map[edge.b].append(i)
        # convert to normal dict
        edge_map = {k: list(v) for k, v in edge_map.items()}
        epsilon = int(data['epsilon'])
        return cls(hole, vertices, edges, dists, edge_map, epsilon)

    def json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


@dataclass
class Pose:
    vertices: List[Point]

    @classmethod
    def from_json(cls, data, dislikes=None):
        assert isinstance(data, dict), f'{data} is not a dict'
        assert tuple(data.keys()) == ('vertices',), f'{data} is not a pose'
        vertices = [Point(x, y) for x, y in data['vertices']]
        return cls(vertices)

    def json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
