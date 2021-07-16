#!/usr/bin/env python3

import os
from collections import namedtuple
from typing import Dict, List, Optional

import matplotlib.pyplot as plt
import requests
from ortools.sat.python.cp_model import CpModel, CpSolver
from shapely.geometry import LineString, Point, Polygon

Coord = namedtuple('Coord', ['x', 'y'])
Pair = namedtuple('Pair', ['ax', 'ay', 'bx', 'by'])

HEADERS = {"Authorization": "Bearer " + os.environ['ICFP2021_API_KEY']}


def dist(a: Coord, b: Coord) -> int:
    ''' Squared distance used in the problem '''
    return (a.x - b.x) ** 2 + (a.y - b.y) ** 2


class Problem:
    def __init__(self, problem_number: int):
        self.problem_number = problem_number
        self.solution = None
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
        self.deltas = {d: self.get_deltas(d) for d in set(self.edge_dists)}

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
            d = self.edge_dists[i]
            self.model.AddAllowedAssignments([xvar, yvar], self.deltas[d])

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
        solver = CpSolver()
        solver.parameters.max_time_in_seconds = 100.0
        status = solver.Solve(self.model)

    def plot(self, fig=None, ax=None):
        ''' Plot the solution '''
        if fig is None or ax is None:
            fig, ax = plt.subplots()
        cycle = self.hole + [self.hole[0]]
        ax.plot([c.x for c in cycle], [c.y for c in cycle], 'k-')
        ax.scatter([p.x for p in self.points], [p.y for p in self.points], s=2)
        if self.solution is not None:
            vert = [Coord(*p) for p in self.solution['vertices']]
            for i, j in self.edges:
                a, b = vert[i], vert[j]
                ax.plot([a.x, b.x], [a.y, b.y], 'r-')
        # Flip since the problem renderings use inverted y
        ax.invert_yaxis()
        # Draw gridlines to help visualise issues with boundaries
        ax.grid(True)
        ax.set_xticks(range(self.bounds.ax, self.bounds.bx + 1))
        ax.set_yticks(range(self.bounds.ay, self.bounds.by + 1))

    def submit(self):
        ''' Upload the submission '''
        assert self.solution is not None
        url = f'https://poses.live/api/problems/{self.problem_number}/solutions'
        r = requests.post(url, headers=HEADERS, json=self.solution)
        r.raise_for_status()

    def dislikes(self, solution=None) -> int:
        ''' Calculate the dislikes for a given solution '''
        vertices = self.solution['vertices']
        return sum(min([dist(h, v) for v in vertices]) for h in self.hole)
