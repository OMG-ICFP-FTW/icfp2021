#!/usr/bin/env python3
import os
import json
import math
from collections import defaultdict
from tqdm import tqdm
from itertools import combinations
from aray.types import Point, Edge
from aray.problem import Problem, Pose
from aray.boxlet import polygon_points
from aray.stretch import slow_stretch
from aray.dislike import dislikes
from aray.util import dist
from aray.forbidden import get_forbidden
from ortools.sat.python import cp_model


def compute_dislikes(hole, pose):
    total_dislike = 0
    for hole_pt in hole:
        total_dislike += min([dsq(hole_pt, pose_pt) for pose_pt in pose])
    return total_dislike


def dsq(v1, v2):
    return (v2[0] - v1[0]) ** 2 + (v2[1] - v1[1])**2


class VarArraySolutionPrinter(cp_model.CpSolverSolutionCallback):
    """Print intermediate solutions."""

    def __init__(self, pose_vertices, hole):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self._pose_vertices = pose_vertices
        self._hole = hole
        self._best_solution = None
        self._least_dislike = None

    def on_solution_callback(self):
        solution = []
        for i, v in self._pose_vertices.items():
            solution.append([self.Value(v[0]), self.Value(v[1])])

        d = compute_dislikes(self._hole, solution)

        if self._least_dislike is None or d < self._least_dislike:
            self._least_dislike = d
            self._best_solution = solution
            print(f"Dislike: {self._least_dislike}")
            print(json.dumps({
                "vertices": self._best_solution,
            }))

    def best_solution(self):
        return self._best_solution, self._least_dislike


def get_solution(problem_number, timeout_seconds=100.0, constraints=-1, get_all=False):

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
        circle = sorted((p.x, p.y) for p in slow_stretch(Pa, Pb, epsilon))
        model.AddAllowedAssignments([xvar, yvar], circle)
    assert len(edges) == len(problem.edges)

    print('getting forbidden edges')
    forbidden_edges = get_forbidden(problem_number)
    print('got forbidden edges')
    assert len(forbidden_edges) == len(
        edges), f'{len(forbidden_edges)} {len(edges)}'
    for f, (a, b) in zip(forbidden_edges, problem.edges):
        vars = [pose[a].x, pose[a].y, pose[b].x, pose[b].y]
        forbid = set()
        for (ax, ay), (bx, by) in f:
            forbid.add((ax, ay, bx, by))
            forbid.add((bx, by, ax, ay))
        model.AddForbiddenAssignments(vars, sorted(forbid))

    if constraints == 0:
        for i, h in enumerate(problem.hole):
            vars = []
            for j, p in enumerate(pose):
                var = model.NewBoolVar(f'H{i}_{j}')
                model.Add(p.x == h.x).OnlyEnforceIf(var)
                model.Add(p.y == h.y).OnlyEnforceIf(var)
                vars.append(var)
            model.AddBoolOr(vars)
    elif constraints > 0:
        hole_vars = []
        for i, h in enumerate(problem.hole):
            hole_var = model.NewBoolVar(f'H{i}')
            vars = []
            for j, p in enumerate(pose):
                var = model.NewBoolVar(f'H{i}_{j}')
                model.Add(p.x == h.x).OnlyEnforceIf(var)
                model.Add(p.y == h.y).OnlyEnforceIf(var)
                vars.append(var)
            model.AddBoolOr(vars).OnlyEnforceIf(hole_var)
            hole_vars.append(hole_var)

        n = len(problem.hole) - constraints
        # get all combinations of hole variables with n
        for comb in combinations(range(len(hole_vars)), n):
            model.AddBoolOr([hole_vars[i] for i in comb])

    # Creates a solver and solves the model.
    print('ready to solve!')
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = timeout_seconds
    print('Solving')
    if get_all:
        pose_vertices = {i: (p.x, p.y) for i, p in enumerate(pose)}
        solution_printer = VarArraySolutionPrinter(pose_vertices, problem.hole)
        status = solver.SearchForAllSolutions(model, solution_printer)
        best, score = solution_printer.best_solution()
        assert score is not None, "failed to find a solution"
        print('got best', best)
        print('got best_score', score)
        print('got status', status)
        vertices = best
        # score = dislikes(problem.hole, vertices)
        # assert score == best_score
        print('score', score)
        # def dislikes(hole: List[Point], points: List[Point]) -> int:
        filename = f'/tmp/{problem_number}-{score}-cpsolver3.json'
        with open(filename, 'w') as f:
            data = dict(vertices=vertices)
            json.dump(data, f)
        print('saved', filename)
    else:
        status = solver.Solve(model)
        print('got status', status)
        vertices = [Point(solver.Value(v.x), solver.Value(v.y)) for v in pose]
        score = dislikes(problem.hole, vertices)
        print('score', score)
        # def dislikes(hole: List[Point], points: List[Point]) -> int:
        filename = f'/tmp/{problem_number}-{score}-cpsolver3.json'
        with open(filename, 'w') as f:
            data = dict(vertices=vertices)
            json.dump(data, f)
        print('saved', filename)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('problem_number', type=int)
    parser.add_argument('-t', '--timeout', type=float, default=1000.0)
    parser.add_argument('-c', '--constraints', type=int, default=-1)
    parser.add_argument('-a', '--get_all', action='store_true')
    args = parser.parse_args()
    get_solution(args.problem_number, args.timeout,
                 args.constraints, args.get_all)
