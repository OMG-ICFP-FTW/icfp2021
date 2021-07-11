#!/usr/bin/env python3
# partial.py - partial solution to the problem

import random
import matplotlib.pyplot as plt
from typing import List, Dict, Optional, Set
from dataclasses import dataclass

from .problem import Problem, Pose
from .types import Point, Edge
from .stretch import stretch
from .boxlet import Boxlet


@dataclass
class Partial:
    problem: Problem
    vertices: List[Optional[Point]]
    edges: List[Edge]  # list of edges in the pose
    dists: List[int]  # squared distance for original edge lengths
    edge_map: Dict[int, List[int]]  # map vertex index -> list of edge indexes
    placement: Set[Point]  # all of the points inside the hole
    epsilon: int

    def get_unplaced_points(self) -> List[int]:
        ''' Get the indices of points yet to be placed '''
        return [i for i, v in enumerate(self.vertices) if v is None]

    def get_random_unplaced_point(self) -> int:
        ''' Get a random unplaced point '''
        return random.choice(self.get_unplaced_points())

    def get_placements_for_point(self, i: int) -> List[Point]:
        ''' Get the locations that a point could be placed at '''
        # start by copying the hole set
        placement_set = self.placement.copy()
        # for each edge, intersect the set with the stretch confinement
        # fig, ax = plt.subplots(figsize=(10, 10))
        # ps = list(placement_set)
        # ax.scatter([p.x for p in ps], [p.y for p in ps])
        for e in self.edge_map[i]:
            edge = self.edges[e]
            point = self.vertices[edge.b if edge.a == i else edge.a]
            if point is not None:
                placement_set &= set(stretch(point, self.dists[e], self.epsilon))
                ps = list(placement_set)
                # ax.scatter([p.x for p in ps], [p.y for p in ps])
        # plt.show()
        return placement_set

    def get_random_placement_for_point(self, i: int) -> Point:
        ''' Get a random placement for a point '''
        return random.choice(list(self.get_placements_for_point(i)))

    def place_point(self, i: int, point: Point):
        ''' Place a point '''
        self.vertices[i] = point

    @classmethod
    def from_problem(cls, problem: Problem):
        ''' Create an empty initial partial solution from a problem '''
        placement = set()
        for boxlet in Boxlet.from_polygon(problem.hole):
            for p in boxlet.iter_points():
                placement.add(p)
        vertices = [None for _ in range(len(problem.vertices))]
        return cls(problem, vertices, edges=problem.edges, dists=problem.dists, edge_map=problem.edge_map, placement=placement, epsilon=problem.epsilon)
