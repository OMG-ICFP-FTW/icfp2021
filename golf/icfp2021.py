#!/usr/bin/env python3

import os
from collections import defaultdict, namedtuple
from typing import Dict, List, Optional
import struct
import subprocess
import json
import matplotlib.pyplot as plt
import requests
from ortools.sat.python.cp_model import CpModel, CpSolver, OPTIMAL, FEASIBLE
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
        self.model = None
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
        # If we're precomputing forbidden edges
        self.forbidden = None  # Will be map from delta -> forbidden

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

    def constrain_zero(self):
        ''' Constrain to zero-dislikes solutions '''
        assert self.model is not None, 'build model first'
        for i, h in enumerate(self.hole):
            vars = []
            for j, p in enumerate(self.pose_vars):
                var = self.model.NewBoolVar(f'H{i}P{j}')
                self.model.Add(h.x == p.x).OnlyEnforceIf(var)
                self.model.Add(h.y == p.y).OnlyEnforceIf(var)
                vars.append(var)
            self.model.AddBoolOr(vars)

    def constrain_translate(self):
        ''' Constrain solution to be a translation of original pose '''
        for i, (j, k) in enumerate(self.edges):
            a, b = self.vertices[j], self.vertices[k]
            xvar, yvar = self.edge_vars[i]
            self.model.Add(xvar == b.x - a.x)
            self.model.Add(yvar == b.y - a.y)

    def hint_translate(self):
        ''' Hint the solution should be a translation of original pose '''
        for i, (j, k) in enumerate(self.edges):
            a, b = self.vertices[j], self.vertices[k]
            xvar, yvar = self.edge_vars[i]
            self.model.AddHint(xvar, b.x - a.x)
            self.model.AddHint(yvar, b.y - a.y)

    def load_forbidden(self):
        ''' Load precomputed forbidden edges '''
        assert self.forbidden is None, 'already loaded'
        filepath = f'/tmp/{self.problem_number}_forbidden_edges.bin'
        if not os.path.exists(filepath):
            cmd = ['/home/aray/code/icfp2021/icfp2021/cc_gang/forbidden',
                   f'{self.problem_number}', f'/tmp/{self.problem_number}.problem']
            print(f'running {cmd}')
            subprocess.check_call(cmd)
        assert os.path.exists(filepath)
        # Read the file into a bytearray
        with open(filepath, 'rb') as f:
            data = bytearray(f.read())
        # Delete the file
        os.remove(filepath)
        assert len(data) % 8 == 0, f'{len(data)} is not multiple of 8'
        forbidden = defaultdict(list)
        for ax, ay, bx, by in struct.iter_unpack('<HHHH', data):
            pair = Pair(ax, ay, bx, by)
            delta = Coord(bx - ax, by - ay)
            forbidden[delta].append(pair)
            # Also add inverse
            pair = Pair(bx, by, ax, ay)
            delta = Coord(ax - bx, ay - by)
            forbidden[delta].append(pair)
        self.forbidden = forbidden

    def constrain_forbidden(self):
        ''' Constrain edges to not be in forbidden set '''
        self.load_forbidden()
        for i, (j, k) in enumerate(self.edges):
            a, b = self.pose_vars[j], self.pose_vars[k]
            vars = [a.x, a.y, b.x, b.y]
            forbidden = []
            for delta in self.deltas[self.edge_dists[i]]:
                forbidden.extend(self.forbidden[delta])
            self.model.AddForbiddenAssignments(vars, forbidden)

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
        valid = True
        for i, (j, k) in enumerate(self.edges):
            a, b = vertices[j], vertices[k]
            if not self.valid_edge(a, b):
                u, v = self.pose_vars[j], self.pose_vars[k]
                self.model.AddForbiddenAssignments(
                    [u.x, u.y, v.x, v.y], [(a.x, a.y, b.x, b.y)])
                valid = False
        return valid

    def solve_iter(self) -> bool:
        ''' Do a single round of solving/validating, return True if solution is valid '''
        status = self.solver.Solve(self.model)
        if status not in (FEASIBLE, OPTIMAL):
            print('Failed to find SAT, status:',
                  self.solver.StatusName(status))
            return False
        vertices = [(self.solver.Value(p.x), self.solver.Value(p.y))
                    for p in self.pose_vars]
        self.solution = {'vertices': vertices}
        return self.valid_solution()

    def solve(self, max_tries=10, plot=False, timeout=100.0) -> bool:
        ''' Get a solution '''
        assert self.model is not None, 'build model first'
        self.solver = CpSolver()
        self.solver.parameters.max_time_in_seconds = timeout
        for i in range(max_tries):
            print('solve iter', i)
            if self.solve_iter():
                break
            if plot:
                self.plot()
        else:
            return False
        return True

    def plot(self, fig=None, ax=None):
        ''' Plot the solution '''
        if fig is None or ax is None:
            fig, ax = plt.subplots(figsize=(4, 4))
        cycle = self.hole + [self.hole[0]]
        # Plot the hole
        ax.plot([c.x for c in cycle], [c.y for c in cycle], 'k-')
        # Plot all of the valid points
        ax.scatter([p.x for p in self.points], [p.y for p in self.points], s=2)
        # Plot our solution if we have one
        if self.solution is not None:
            vert = [Coord(*p) for p in self.solution['vertices']]
            for i, j in self.edges:
                a, b = vert[i], vert[j]
                color = 'g-' if self.valid_edge(a, b) else 'r-'
                ax.plot([a.x, b.x], [a.y, b.y], color)
        ax.invert_yaxis()  # Flip since the problem renderings use inverted y
        plt.show()

    def submit(self):
        ''' Upload the submission '''
        assert self.solution is not None
        url = f'https://poses.live/api/problems/{self.problem_number}/solutions'
        r = requests.post(url, headers=self.get_headers(), json=self.solution)
        r.raise_for_status()

    def dislikes(self, solution=None) -> int:
        ''' Calculate the dislikes for a given solution '''
        vertices = [Coord(*p) for p in self.solution['vertices']]
        return sum(min([dist(h, v) for v in vertices]) for h in self.hole)


if __name__ == '__main__':
    for problem_number in range(2,132):
        print('Loading problem', problem_number)
        problem = Problem(problem_number)
        print('Building model')
        problem.build_model()
        print('Adding forbidden edge constraints')
        problem.constrain_forbidden()
        print('Solving')
        if problem.solve(max_tries=1, timeout=1000.0):
            print('Submitting, expect score:', problem.dislikes())
            problem.submit()
        print('Finished')
