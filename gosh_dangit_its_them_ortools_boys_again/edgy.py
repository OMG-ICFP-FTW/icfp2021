#!/usr/bin/env python3
import os
import json
from collections import defaultdict
from tqdm import tqdm
from aray.types import Point, Edge
from aray.problem import Problem, Pose
from aray.boxlet import polygon_points
from aray.stretch import delta_stretch, center_stretch
from aray.dislike import dislikes
from aray.util import dist
from aray.forbidden import get_forbidden
from ortools.sat.python import cp_model


def orient(p: Point, q: Point, r: Point):
    ''' Get orientation of triangle pqr (Collinear, Clockwise, Counterclockwise) '''
    val = (q.y - p.y) * (r.x - q.x) - (q.x - p.x) * (r.y - q.y)
    return 0 if val == 0 else (1 if val > 0 else 2)


def intersect(a: Point, b: Point, c: Point, d: Point) -> bool:
    ''' Return True if segments a-b and c-d have a crossing intersection '''
    # https://www.geeksforgeeks.org/check-if-two-given-line-segments-intersect/
    return orient(a, b, c) != orient(a, b, d) and orient(c, d, a) != orient(c, d, b)


class VarArraySolutionPrinter(cp_model.CpSolverSolutionCallback):
    """Print intermediate solutions."""

    def __init__(self, variables):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.__variables = variables
        self.__solution_count = 0

    def on_solution_callback(self):
        self.__solution_count += 1
        for v in self.__variables:
            print('%s=%i' % (v, self.Value(v)), end=' ')
        print()

    def solution_count(self):
        return self.__solution_count


def get_solution(problem_number, timeout_seconds=100.0, zero=False):
    model = cp_model.CpModel()

    problem = Problem.get(problem_number)
    epsilon = problem.epsilon
    points = polygon_points(problem.hole)
    placement = sorted((p.x, p.y) for p in points)
    xmin = min(p.x for p in points)
    xmax = max(p.x for p in points)
    ymin = min(p.y for p in points)
    ymax = max(p.y for p in points)
    dx = xmax - xmin
    dy = ymax - ymin
    print('xmin', xmin, 'xmax', xmax, 'ymin',
          ymin, 'ymax', ymax, 'dx', dx, 'dy', dy)

    pose = []
    for i, v in enumerate(problem.vertices):
        xvar = model.NewIntVar(xmin, xmax, 'V%i_x' % i)
        yvar = model.NewIntVar(ymin, ymax, 'V%i_y' % i)
        pose.append(Point(xvar, yvar))
        # Add constraint that vertex is inside placement
        model.AddAllowedAssignments([xvar, yvar], placement)
    assert len(pose) == len(problem.vertices)

    edges = []
    for i, (a, b) in enumerate(problem.edges):
        xvar = model.NewIntVar(-dx, dx, 'E%i_dx' % i)
        yvar = model.NewIntVar(-dy, dy, 'E%i_dy' % i)
        edges.append(Point(xvar, yvar))  # since we reference with .x and .y
        # Add constraints that dx = u.x - v.x and dy = u.y - v.y
        model.Add(xvar == pose[a].x - pose[b].x)
        model.Add(yvar == pose[a].y - pose[b].y)
        # Add contraints that the deltas must be in a given set
        Pa, Pb = problem.vertices[a], problem.vertices[b]
        circle = sorted((p.x, p.y) for p in delta_stretch(Pa, Pb, epsilon))
        model.AddAllowedAssignments([xvar, yvar], circle)
    assert len(edges) == len(problem.edges)

    forbidden_edges = get_forbidden(problem_number)
    assert len(forbidden_edges) == len(edges), f'{len(forbidden_edges)} {len(edges)}'
    for f, (a, b) in zip(forbidden_edges, problem.edges):
        vars = [pose[a].x, pose[a].y, pose[b].x, pose[b].y]
        forbid = set()
        for (ax, ay), (bx, by) in f:
            forbid.add((ax, ay, bx, by))
            forbid.add((bx, by, ax, ay))
        model.AddForbiddenAssignments(vars, sorted(forbid))

    # Hole == 0 
    if zero:
        for i, h in enumerate(problem.hole):
            vars = []
            for j, p in enumerate(pose):
                var = model.NewBoolVar(f'H{i}_{j}')
                model.Add(p.x == h.x).OnlyEnforceIf(var)
                model.Add(p.y == h.y).OnlyEnforceIf(var)
                vars.append(var)
            model.AddBoolOr(vars)

    # Creates a solver and solves the model.
    print('ready to solve!')
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = timeout_seconds
    print('Solving')
    status = solver.Solve(model)

    print('status =', solver.StatusName(status))
    for v in pose + edges:
        print(v.x.Name(), '=', solver.Value(v.x))
        print(v.y.Name(), '=', solver.Value(v.y))

    vertices = [Point(solver.Value(v.x), solver.Value(v.y)) for v in pose]
    score = dislikes(problem.hole, vertices)
    print('score', score)
    # def dislikes(hole: List[Point], points: List[Point]) -> int:
    filename = f'/tmp/{problem_number}-{score}-cpsolver2.json'
    with open(filename, 'w') as f:
        points = [[p.x, p.y] for p in vertices]
        data = dict(vertices=vertices)
        json.dump(data, f)
    print('saved', filename)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('problem_number', type=int)
    parser.add_argument('-t', '--timeout', type=float, default=1000.0)
    parser.add_argument('-z', '--zero', action='store_true')
    args = parser.parse_args()
    get_solution(args.problem_number, args.timeout, args.zero)
