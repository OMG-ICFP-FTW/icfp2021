#!/usr/bin/env python

# %%
import json
import os
from collections import namedtuple
from typing import Dict, List, NamedTuple, Tuple

import matplotlib.pyplot as plt
import requests
from aray.problem import Problem
from ortools.sat.python.cp_model import (CpModel, CpSolver,
                                         CpSolverSolutionCallback, IntVar)
from shapely.geometry import LineString, Point, Polygon

Coord = namedtuple('Point', ['x', 'y'])
Pair = namedtuple('Pair', ['ax', 'ay', 'bx', 'by'])


class SolutionCollector(CpSolverSolutionCallback):
    def __init__(self, variables):
        super(SolutionCollector, self).__init__()
        self.variables = variables
        self.solutions = []

    def on_solution_callback(self):
        self.solutions.append([self.Value(v) for v in self.variables])


def get_problem(problem_number: int) -> Dict:
    ''' Get a problem JSON, downloading it if not already downloaded '''
    problem_dir = os.path.join(os.path.dirname(__file__), '../problems')
    os.makedirs(problem_dir, exist_ok=True)
    filename = os.path.join(problem_dir, f'{problem_number}.json')
    if not os.path.exists(filename):
        hdr = {"Authorization": "Bearer " + os.environ['ICFP2021_API_KEY']}
        r = requests.get(f"https://poses.live/api/problems/{i}", headers=hdr)
        r.raise_for_status()
        with open(filename, 'w') as f:
            json.dump(r.json(), f)
    with open(filename, 'r') as f:
        return json.load(f)


def get_bounds(hole: List[Point]) -> Pair:
    ''' Get the x and y limits of our problem '''
    xs, ys = [p.x for p in hole], [p.y for p in hole]
    return Pair(min(xs), min(ys), max(xs), max(ys))


def get_points(bounds: Pair, poly: Polygon) -> List[Point]:
    ''' Get all of the integer points valid for a problem '''
    points = []
    for x in range(bounds.ax, bounds.bx + 1):
        for y in range(bounds.ay, bounds.by + 1):
            if poly.intersects(Point(x, y)):
                points.append(Point(x, y))
    return sorted(points)


def get_dists(edges: List[Tuple[int, int]], vertices: List[Point]) -> List[int]:
    ''' Returns the distance of each edge '''
    edge_dists = []
    for i, j in edges:
        a, b = vertices[i], vertices[j]
        dist = (a.x - b.x) ** 2 + (a.y - b.y) ** 2
        edge_dists.append(dist)
    return edge_dists  # must be in original edge order


def get_deltas(d_old: int, epsilon: int) -> List[Coord]:
    ''' Get all of the valid delta x,y pairs for a given original edge '''
    deltas = []
    n = int(d_old ** 0.5 + 1) * 2
    for x in range(-n, n + 1):
        for y in range(-n, n + 1):
            d_new = x ** 2 + y ** 2
            if abs(d_new / d_old - 1) <= epsilon / 1e6:
                deltas.append(Coord(x, y))
    return sorted(deltas)


def get_forbidden(points: List[Point], poly: Polygon, delta: Coord) -> List[Pair]:
    ''' Given a delta, get all of the illegal pairs of points with that delta '''
    forbidden = []
    for a in points:
        b = Point(a.x + delta.x, a.y + delta.y)
        if b not in points:
            continue
        ab = LineString((a, b))
        if poly.contains(ab) or ab.within(poly):
            continue
        elif poly.exterior.crosses(ab) or (poly.touches(ab) and not poly.exterior.contains(ab)):
            forbidden.append(Pair(a.x, a.y, b.x, b.y))
    return sorted(forbidden)


def get_pose_vars(num_vertices: int, bounds: Pair, model: CpModel) -> List[Coord]:
    ''' Get the pose position (x, y) variables we'll solve for '''
    pose = []
    for i in range(num_vertices):
        xvar = model.NewIntVar(bounds.ax, bounds.bx, 'P%ix' % i)
        yvar = model.NewIntVar(bounds.ay, bounds.by, 'P%iy' % i)
        pose.append((xvar, yvar))
    return pose


def get_edge_vars(bounds: Pair, edges: List[Tuple[int, int]], model: CpModel) -> List[Coord]:
    ''' Get the edge variables, which are deltas between connected points '''
    edge_vars = []
    dx, dy = bounds.bx - bounds.ax, bounds.by - bounds.ay
    for i, (a, b) in enumerate(edges):
        xvar = model.NewIntVar(-dx, dx, 'E%idx' % i)
        yvar = model.NewIntVar(-dy, dy, 'E%idy' % i)
        edge_vars.append(Coord(xvar, yvar))
    return edge_vars


def solve(problem_number: int, timeout_seconds: float = 1000.0):
    # Problem data
    problem = get_problem(problem_number)
    hole = problem['hole']
    edges = problem['figure']['edges']
    vertices = problem['figure']['vertices']
    epsilon = problem['epsilon']
    # Computed data
    bounds = get_bounds(hole)
    poly = Polygon(hole)
    points = get_points(bounds, poly)
    edge_dists = get_dists(edges, vertices)
    all_dists = set(edge_dists)
    deltas = {d: get_deltas(d, epsilon) for d in all_dists}
    all_deltas = set(sum(deltas.values(), []))
    forbidden = {d: get_forbidden(points, poly, d) for d in all_deltas}
    # Solve
    solver = CpSolver()
    model = CpModel()
    solver.parameters.max_time_in_seconds = timeout_seconds
    pose_vars = get_pose_vars(len(vertices), bounds, model)
    edge_vars = get_edge_vars(bounds, edges, pose_vars)
    # TODO: have to flatten vars before passing to collector


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('problem_number', type=int)
    parser.add_argument('-t', '--timeout_seconds', type=float, default=1000.0)
    args = parser.parse_args()
    solve(args.problem_number, args.timeout)
