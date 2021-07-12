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
from ortools.sat.python import cp_model


def orient(p: Point, q: Point, r: Point):
    ''' Get orientation of triangle pqr (Collinear, Clockwise, Counterclockwise) '''
    val = (q.y - p.y) * (r.x - q.x) - (q.x - p.x) * (r.y - q.y)
    return 0 if val == 0 else (1 if val > 0 else 2)


def intersect(a: Point, b: Point, c: Point, d: Point) -> bool:
    ''' Return True if segments a-b and c-d have a crossing intersection '''
    # https://www.geeksforgeeks.org/check-if-two-given-line-segments-intersect/
    return orient(a, b, c) != orient(a, b, d) and orient(c, d, a) != orient(c, d, b)


def get_solution(problem_number):
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

    # precompute hole edge x and y margins
    hole = problem.hole  # list of points
    hole_edges = [(hole[i], hole[(i + 1) % len(hole)])
                  for i in range(len(hole))]
    hole_edges_x = defaultdict(set)  # map from x coordinate to hole edge index
    hole_edges_y = defaultdict(set)  # map from y coordinate to hole edge index
    for i, (u, v) in enumerate(hole_edges):
        for x in range(min(u.x, v.x), max(u.x, v.x) + 1):
            hole_edges_x[x].add(i)
        for y in range(min(u.y, v.y), max(u.y, v.y) + 1):
            hole_edges_y[y].add(i)

    # precompute edge distances
    distances = defaultdict(list)  # map from distance -> list of edge indexes
    for i, (a, b) in enumerate(problem.edges):
        distances[dist(problem.vertices[a], problem.vertices[b])].append(i)
    print('distances', distances)

    # big computation, add concavity exclusions for every edge
    forbidden = defaultdict(set)  # map from distance -> tuple of forbidden point assignments
    for d, edge_idxs in distances.items():  # only do this for unique distances
        print('distance', d, 'edges', edge_idxs)
        circle = center_stretch(d, epsilon)  # set of points in the distance circle
        print('placement size', len(placement))
        for ax, ay in tqdm(placement):  # start for every valid point in placement
            a = Point(ax, ay)
            for c in circle:  # for every delta in our valid circle points
                b = Point(a.x + c.x, a.y + c.y)  # get our end coordinate
                if b not in placement: # both ends must be inside placement
                    continue
                # if opposite corners are valid
                # get all of the hole edges to consider intersecting with a, b
                hole_edge_idxs = set()
                for x in range(min(a.x, b.x), max(a.x, b.x) + 1):
                    hole_edge_idxs.update(hole_edges_x[x])
                for y in range(min(a.y, b.y), max(a.y, b.y) + 1):
                    hole_edge_idxs.update(hole_edges_y[y])
                # for each hole edge, check for intersection
                for i in hole_edge_idxs:
                    u, v = hole_edges[i]  # indexes to hole points
                    if intersect(a, b, u, v):
                        forbidden[d].add((a.x, a.y, b.x, b.y))
                        forbidden[d].add((b.x, b.y, a.x, a.y))
    print('forbidden', forbidden)
    

    assert False

    # Creates a solver and solves the model.
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    print('status =', solver.StatusName(status))
    for v in pose + edges:
        print(v.x.Name(), '=', solver.Value(v.x))
        print(v.y.Name(), '=', solver.Value(v.y))

    vertices = [Point(solver.Value(v.x), solver.Value(v.y)) for v in pose]
    score = dislikes(problem.hole, vertices)
    print('score', score)
    # def dislikes(hole: List[Point], points: List[Point]) -> int:
    filename = f'/tmp/{problem_number}-{score}-cpsolver.json'
    with open(filename, 'w') as f:
        points = [[p.x, p.y] for p in vertices]
        data = dict(vertices=vertices)
        json.dump(data, f)
    print('saved', filename)


if __name__ == '__main__':
    import sys
    get_solution(int(sys.argv[1]))
