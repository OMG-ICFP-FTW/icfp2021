#!/usr/bin/env python3

import os
from collections import defaultdict, namedtuple
from typing import Dict, List, Optional
import struct
import subprocess
import json
import matplotlib.pyplot as plt
import requests
from shapely.geometry import LineString, Point, Polygon

Coord = namedtuple('Coord', ['x', 'y'])
Pair = namedtuple('Pair', ['ax', 'ay', 'bx', 'by'])


def dist(a: Coord, b: Coord) -> int:
    ''' Squared distance used in the problem '''
    return (a.x - b.x) ** 2 + (a.y - b.y) ** 2


class Problem:
    def __init__(self, problem_number: int):
        self.problem_number = problem_number
        self.solution = None
        problem = self.get_problem()
        self.hole = [Coord(x, y) for x, y in problem['hole']]
        self.vertices = [Coord(x, y) for x, y in problem['figure']['vertices']]
        self.edges = problem['figure']['edges']
        self.epsilon = problem['epsilon']
        # Compute geometry
        self.bound = self.get_bound()
        self.poly = Polygon(self.hole)
        self.points = self.get_points()
        self.edge_dists = [self.edge_dist(i) for i in range(len(self.edges))]
        self.deltas = {d: self.get_deltas(d) for d in set(self.edge_dists)}

    def get_headers(self) -> Dict:
        ''' Get the headers to interact with API '''
        api_key = os.environ['ICFP2021_API_KEY']
        return {"Authorization": "Bearer " + api_key}

    def get_problem(self) -> Dict:
        ''' Download a problem JSON or load from cache '''
        filepath = f'/tmp/{self.problem_number}.problem'
        if not os.path.exists(filepath):
            problem_url = f"https://poses.live/api/problems/{self.problem_number}"
            r = requests.get(problem_url, headers=self.get_headers())
            r.raise_for_status()
            with open(filepath, 'w') as f:
                json.dump(r.json(), f)
        with open(filepath) as f:
            return json.load(f)

    def get_bound(self) -> Pair:
        ''' Get the bound of our solution xs and ys '''
        xs, ys = [h.x for h in self.hole], [h.y for h in self.hole]
        return Pair(min(xs), min(ys), max(xs), max(ys))

    def get_points(self) -> List[Coord]:
        ''' Get all valid points for the solution pose '''
        points = []
        for x in range(self.bound.ax, self.bound.bx + 1):
            for y in range(self.bound.ay, self.bound.by + 1):
                if self.poly.intersects(Point(x, y)):
                    points.append(Coord(x, y))
        return points

    def edge_dist(self, i: int) -> int:
        ''' Get the squared distance of edge at index i '''
        j, k = self.edges[i]
        return dist(self.vertices[j], self.vertices[k])

    def get_deltas(self, d: int) -> List[Coord]:
        ''' Get all valid delta x,y for a given distance and epsilon '''
        n = int(d ** 0.5 + 1) * 2
        deltas = []
        for x in range(-n, n + 1):
            for y in range(-n, n + 1):
                if abs((x ** 2 + y ** 2) / d - 1) <= (self.epsilon / 1e6):
                    deltas.append(Coord(x, y))
        return deltas

    def valid_edge(self, a: Coord, b: Coord) -> bool:
        ''' Returns True if this is a valid edge, else False '''
        ab = LineString((a, b))
        if self.poly.contains(ab) or ab.within(self.poly):
            return True
        elif self.poly.exterior.crosses(ab):
            return False
        elif self.poly.touches(ab) and not self.poly.exterior.contains(ab):
            return False
        return True

    def valid_solution(self) -> bool:
        ''' Return True if solution is invalid, otherwise False and add constraints '''
        vertices = [Coord(*p) for p in self.solution['vertices']]
        for i, (j, k) in enumerate(self.edges):
            a, b = vertices[j], vertices[k]
            if not self.valid_edge(a, b):
                return False
        return True

