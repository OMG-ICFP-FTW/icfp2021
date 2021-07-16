#!/usr/bin/env python3

import os
from collections import namedtuple
from typing import Dict, List

import matplotlib.pyplot as plt
import requests
from ortools.sat.python.cp_model import CpModel, CpSolver
from shapely.geometry import LineString, Point, Polygon

Coord = namedtuple('Coord', ['x', 'y'])
Pair = namedtuple('Pair', ['ax', 'ay', 'bx', 'by'])

headers = {"Authorization": "Bearer " + os.environ['ICFP2021_API_KEY']}


def get_problem(n: int) -> Dict:
    ''' Download a problem JSON '''
    r = requests.get(f"https://poses.live/api/problems/{n}", headers=headers)
    r.raise_for_status()
    return r.json()


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


for PROBLEM_NUMBER in range(1, 133):
    # Computed data
    hole = problem['hole']
    edges = problem['figure']['edges']
    vertices = problem['figure']['vertices']
    epsilon = problem['epsilon']
    xs, ys = [p[0] for p in hole], [p[1] for p in hole]
    poly = Polygon(hole)
    points = [(x, y) for x in range(min(xs), max(xs) + 1)
              for y in range(min(ys), max(ys) + 1) if poly.intersects(Point(x, y))]
    edge_dists = [(vertices[i][0] - vertices[j][0]) ** 2 +
                  (vertices[i][1] - vertices[j][1]) ** 2 for i, j in edges]
    deltas = {d: get_deltas(d, epsilon) for d in set(edge_dists)}
    forbidden = {delta: get_forbidden(points, poly, delta)
                 for delta in set(sum(deltas.values(), []))}
    # Constraint Model
    model = CpModel()
    pose = [(model.NewIntVar(min(xs), max(xs), f'P{i}x'), model.NewIntVar(
        min(ys), max(ys), f'P{i}y')) for i in range(len(vertices))]
    [model.AddAllowedAssignments([x, y], points) for x, y in pose]
    dx, dy = max(xs) - min(xs), max(ys) - min(ys)
    for i, (d, (j, k)) in enumerate(zip(edge_dists, edges)):
        xvar, yvar = model.NewIntVar(-dx, dx,
                                     f'E{i}x'), model.NewIntVar(-dy, dy, f'E{i}y')
        model.Add(xvar == pose[j][0] - pose[k][0])
        model.Add(yvar == pose[j][1] - pose[k][1])
        model.AddAllowedAssignments([xvar, yvar], deltas[d])
        model.AddForbiddenAssignments(
            pose[j] + pose[k], sorted(set(sum((forbidden[delta] for delta in deltas[d]), []))))
    # Solver
    solver = CpSolver()
    solver.parameters.max_time_in_seconds = 100.0
    status = solver.Solve(model)
    solution = dict(
        vertices=[(solver.Value(p[0]), solver.Value(p[1])) for p in pose])
    solution
    # Visualize
    fig, ax = plt.subplots()
    cycle = hole + [hole[0]]
    ax.plot([c[0] for c in cycle], [c[1] for c in cycle])
    ax.scatter([p[0] for p in points], [p[1] for p in points], s=2)
    ax.plot([p[0] for p in solution['vertices']], [p[1]
            for p in solution['vertices']], 'go-')
    # Submit
    r = requests.post(
        f'https://poses.live/api/problems/{PROBLEM_NUMBER}/solutions', headers=headers, json=solution)
    r.raise_for_status()
