#!/usr/bin/env python3

import os
from collections import namedtuple
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import requests
from ortools.sat.python.cp_model import CpModel, CpSolver
from shapely.geometry import LineString, Point, Polygon

Coord = namedtuple('Coord', ['x', 'y'])
Pair = namedtuple('Pair', ['ax', 'ay', 'bx', 'by'])

HEADERS = {"Authorization": "Bearer " + os.environ['ICFP2021_API_KEY']}


class Problem:
    def __init__(self, problem_number: int):
        self.problem_number = problem_number
        problem = self.download()
        self.hole = [Coord(x, y) for x, y in problem['hole']]
        self.vertices = [Coord(x, y) for x, y in problem['figure']['vertices']]
        self.edges = problem['figure']['edges']
        self.epsilon = problem['epsilon']
        # Compute geometry
        self.bound = self.get_bound()
        self.poly = Polygon(self.hole)
        self.points = self.get_points()
        self.edge_dists = [self.edge_dist(i) for i in range(len(self.edges))]
        self.deltas = {dist: get_deltas(dist) for dist in set(self.edge_dists)}

    def download(self) -> Dict:
        ''' Download a problem JSON '''
        problem_url = f"https://poses.live/api/problems/{self.problem_number}"
        r = requests.get(problem_url, headers=HEADERS)
        r.raise_for_status()
        return r.json()

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
                    points.append(Point(x, y))
        return points

    def edge_dist(self, i: int) -> int:
        ''' Get the squared distance of edge at index i '''
        j, k = self.edges[i]
        a, b = self.vertices[j], self.vertices[k]
        return (a.x - b.x) ** 2 + (a.y - b.y) ** 2

    def get_deltas(self, d_old: int) -> List[Coord]:
        ''' Get the valid delta x,y for a given distance '''
        n = int(d_old ** 0.5 + 1) * 2
        deltas = []
        for x in range(-n, n + 1):
            for y in range(-n, n + 1):
                if abs((x ** 2 + y ** 2) / d_old - 1) <= (self.epsilon / 1e6):
                    deltas.append(Coord(x, y))
        return deltas

    def get_pose_vars(self) -> List[Coord]:
        ''' Get x, y pairs of our optimization variables '''
        pose = []
        for i in range(len(self.vertices)):
            # Optimization variables for x, y coordinates of pose vertices
            xvar = self.model.NewIntVar(self.bound.ax, self.bound.bx, f'P{i}x')
            yvar = self.model.NewIntVar(self.bound.ay, self.bound.by, f'P{i}y')
            # Constrain pose points to be in set of valid points
            self.model.AddAllowedAssignments([xvar, yvar], self.points)

            pose.append(Coord(xvar, yvar))
        return pose

    def get_edge_vars(self) -> List[Coord]:
        ''' Get the delta x, y variables we will use to constrain edges '''
        dx, dy = self.bound.bx - self.bound.ax, self.bound.by - self.bound.ay
        edge_vars = []
        for i, (j, k) in enumerate(self.edges):
            # Optimization variables for pose edges (delta x, delta y)
            xvar = self.model.NewIntVar(-dx, dx, f'E{i}x')
            yvar = self.model.NewIntVar(-dy, dy, f'E{i}y')
            # Constrain varibles to be the difference between points
            a, b = self.pose_vars[j], self.pose_vars[k]
            self.model.Add(xvar == b.x - a.x)
            self.model.Add(yvar == b.y - a.y)
            # Constrain edges to be in set of valid deltas for given distance
            dist = self.edge_dists[i]
            self.model.AddAllowedAssignments([xvar, yvar], self.deltas[dist])

            edge_vars.append(Coord(xvar, yvar))
        return edge_vars

    def build_model(self):
        ''' Initial construction of our constraints '''
        self.model = CpModel()
        self.pose_vars = self.get_pose_vars()
        self.edge_vars = self.get_edge_vars()

    def valid_edge(a: Coord, b: Coord, points: List[Coord], poly: Polygon) -> bool:
        ''' Returns True if this is a valid edge, else False '''
        assert a in points and b in points, 'invalid edge check'
        ab = LineString((a, b))
        if poly.contains(ab) or ab.within(poly):
            return True
        elif poly.exterior.crosses(ab):
            return False
        elif poly.touches(ab) and not poly.exterior.contains(ab):
            return False
        return True

    def solve(self):
        ''' Get a solution '''
        pass


def get_bound(hole: List[Point]) -> Pair:
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


def get_deltas(d_old: int, epsilon: int) -> List[Coord]:
    ''' Get the valid delta x,y for a given distance '''
    n = int(d_old ** 0.5 + 1) * 2
    deltas = []
    for x in range(-n, n + 1):
        for y in range(-n, n + 1):
            if abs((x ** 2 + y ** 2) / d_old - 1) <= (epsilon / 1e6):
                deltas.append(Coord(x, y))
    return deltas


def valid_edge(a: Coord, b: Coord, points: List[Coord], poly: Polygon) -> bool:
    ''' Returns True if this is a valid edge, else False '''
    assert a in points and b in points, 'invalid edge check'
    ab = LineString((a, b))
    if poly.contains(ab) or ab.within(poly):
        return True
    elif poly.exterior.crosses(ab):
        return False
    elif poly.touches(ab) and not poly.exterior.contains(ab):
        return False
    return True


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


def get_pose_vars(n: int, bounds: Pair, points: List[Coord], model: CpModel) -> List[Coord]:
    ''' Get the pose position (x, y) variables we'll solve for, constrained to points '''
    pose = []
    for i in range(n):
        xvar = model.NewIntVar(bounds.ax, bounds.bx, f'V{i}x')
        yvar = model.NewIntVar(bounds.ay, bounds.by, f'V{i}y')
        model.AddAllowedAssignments([xvar, yvar], points)
        pose.append((xvar, yvar))
    return pose


def get_edge_vars(bounds: Pair, edges: List[Tuple[int, int]], model: CpModel) -> List[Coord]:
    ''' Get the edge variables, which are deltas between connected points '''
    edge_vars = []
    dx, dy = bounds.bx - bounds.ax, bounds.by - bounds.ay
    for i, (a, b) in enumerate(edges):
        xvar = model.NewIntVar(-dx, dx, f'E{i}x')
        yvar = model.NewIntVar(-dy, dy, f'E{i}y')
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
    pose_vars = get_pose_vars(len(vertices), bounds, points, model)
    edge_vars = get_edge_vars(bounds, edges, pose_vars)
    # TODO: have to flatten vars before passing to collector


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('problem_number', type=int)
    parser.add_argument('-t', '--timeout_seconds', type=float, default=1000.0)
    args = parser.parse_args()
    solve(args.problem_number, args.timeout)
