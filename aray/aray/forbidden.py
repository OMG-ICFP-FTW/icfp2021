#!/usr/bin/env python3
# forbidden.py - calculate forbidden edge assignments
#!/usr/bin/env python3
import os
import json
from typing import List, Tuple, Set, NamedTuple
from collections import defaultdict, namedtuple
from tqdm import tqdm
from aray.types import Point, Pair
from aray.problem import Problem, Pose, BASE_PATH
from aray.boxlet import polygon_points
from aray.stretch import delta_stretch, center_stretch
from aray.dislike import dislikes
from aray.util import dist


def orient(p: Point, q: Point, r: Point):
    ''' Get orientation of triangle pqr (Collinear, Clockwise, Counterclockwise) '''
    val = (q.y - p.y) * (r.x - q.x) - (q.x - p.x) * (r.y - q.y)
    return 0 if val == 0 else (1 if val > 0 else 2)


def intersect(a: Point, b: Point, c: Point, d: Point) -> bool:
    ''' Return True if segments a-b and c-d have a crossing intersection '''
    # https://www.geeksforgeeks.org/check-if-two-given-line-segments-intersect/
    o1 = orient(a, b, c)
    o2 = orient(a, b, d)
    o3 = orient(c, d, a)
    o4 = orient(c, d, b)
    if o1 == 0 or o2 == 0 or o3 == 0 or o4 == 0:
        return False
    return (o1 != o2 and o3 != o4)


def forbidden(hole: List[Point], edges: List[Pair], epsilon: int) -> List[List[Pair]]:
    """ Compute the set of forbidden point assignments for an edge """
    # compute hole edges
    hole_points: Set[Point] = polygon_points(hole)
    hole_edges = [Pair(hole[i], hole[(i + 1) % len(hole)])
                  for i in range(len(hole))]
    # print('hole_edges', hole_edges)

    # precompute hole edge x and y margins
    hole_edges_x = defaultdict(set)  # map from x -> set(hole edge indexes)
    hole_edges_y = defaultdict(set)  # map from y -> set(hole edge indexes)
    for i, (u, v) in enumerate(hole_edges):
        for x in range(min(u.x, v.x), max(u.x, v.x) + 1):
            hole_edges_x[x].add(i)
        for y in range(min(u.y, v.y), max(u.y, v.y) + 1):
            hole_edges_y[y].add(i)
    # print('hole_edges_x', hole_edges_x)
    # print('hole_edges_y', hole_edges_y)

    # precompute edge distances
    edge_distances = [dist(a, b) for a, b in edges]
    distances = defaultdict(list)  # map from distance -> list of edge indexes
    for i, d in enumerate(edge_distances):
        distances[d].append(i)
    # print('distances', distances)

    # big computation, add concavity exclusions for every edge
    forbidden = defaultdict(set)  # map from distance -> set of forbidden pairs
    for d in tqdm(sorted(distances.keys())):  # only for unique distances
        circle = center_stretch(d, epsilon)  # set of points in the circle
        for a in hole_points:  # start for every valid point in placement
            for c in circle:  # for every delta in our valid circle points
                b = Point(a.x + c.x, a.y + c.y)  # get our end coordinate
                if b not in hole_points:  # both ends must be inside placement
                    continue
                # get all of the hole edges to consider intersecting with a, b
                hole_edge_idxs = set()
                for x in range(min(a.x, b.x), max(a.x, b.x) + 1):
                    hole_edge_idxs.update(hole_edges_x[x])
                for y in range(min(a.y, b.y), max(a.y, b.y) + 1):
                    hole_edge_idxs.update(hole_edges_y[y])
                # for each hole edge, check for intersection
                for i in hole_edge_idxs:
                    u, v = hole_edges[i]  # unpack pair of points
                    # first check if either points match
                    if a == u or a == v or b == u or b == v:
                        continue
                    # check if edge intersects with a-b
                    if intersect(a, b, u, v):
                        forbidden[d].add(Pair(a, b))
    # print('forbidden', forbidden)

    # convert back to list of edges
    forbidden_edges = [sorted(forbidden[d]) for d in edge_distances]
    # print('forbidden_edges', forbidden_edges)

    return forbidden_edges


def get_forbidden(problem_number):
    filepath = f'/tmp/{problem_number}-forbidden.json'
    if not os.path.exists(filepath):
        problem = Problem.get(problem_number)
        vertices = problem.vertices
        edges = [Pair(vertices[a], vertices[b]) for a, b in problem.edges]
        forbidden_edges = forbidden(problem.hole, edges, problem.epsilon)
        with open(filepath, 'w') as f:
            json.dump(forbidden_edges, f)
        print('wrote', filepath)
    with open(filepath, 'r') as f:
        data = json.load(f) 
    # need to convert back to pairs
    return [[Pair(Point(*a), Point(*b)) for a, b in d] for d in data]


if __name__ == '__main__':
    import sys
    problem_number = int(sys.argv[1])
    print(get_forbidden(problem_number))