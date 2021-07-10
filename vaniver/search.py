import json
import math
import os
import random

import numpy as np

PROBLEM_FILEDIR = "problems"
SOLUTION_FILEDIR = "solutions"

def dist(a, b):
    return (a[0]-b[0])**2 + (a[1]-b[1])**2

class hole():
    def __init__(self, vertices):
        self.vertices = vertices
        self.vertex_cycle = self.vertices + [self.vertices[0]]
        self.edges = list(zip(self.vertex_cycle[:-1], self.vertex_cycle[1:]))

    def inside(self, point):
        """Given a list of (x,y) pairs in hole, calculate the winding number of the vectors from point to those pairs in hole."""
        x, y = point
        sum_theta = 0
        for h in self.vertex_cycle:
            x1, y1 = h
            sum_theta += math.atan2(y1-y, x1-x)
        return abs(sum_theta) < math.pi / 2

    def calc_dislikes(self, positions):
        """Calculates the minimum distance to a vertex in positions for each vertex in the hole."""
        sum_dislikes = 0
        for h in self.vertices:
            sum_dislikes += min([dist(h, v) for v in positions])
        return sum_dislikes

class figure():
    def __init__(self, problem):
        self.edges = problem["figure"]["edges"]
        self.vertices = problem["figure"]["vertices"]
        self.edge_dists = []
        for edge in self.edges:
            edge_dist = dist(self.vertices[edge[0]], self.vertices[edge[1]])
            self.edge_dists.append([edge_dist * (1 - problem["epsilon"]/1000000.0), edge_dist * (1 + problem["epsilon"]/1000000.0)])

class pose():
    def __init__(self, hole, figure):
        self.hole = hole
        self.figure = figure
        self.valid = self.check_valid()
        self.dislikes = self.calc_dislikes()

    def check_valid(self):
        """Determines whether the figure fits within the hole. Checks both vertices and edges."""
        for edge in self.figure.edges:
            edge1 = self.figure.vertices[edge[0]]
            edge2 = self.figure.vertices[edge[1]]
            if not self.hole.inside(edge1):
                return False
            if not self.hole.inside(edge2):
                return False
            for hedge in self.hole.edges:
                if check_line_intersection([edge1, edge2], hedge):
                    return False 
        return True

    def calc_dislikes(self):
        return self.hole.calc_dislikes(self.figure.vertices)

    def move(self, vertex, x, y):
        """Move a single point by x,y, then recheck validity. """

def check_line_intersection(line1, line2):
    """Given two line segments (each defined by two (x,y) pairs), return true if the two segments intersect and false if they do not."""
    x1, y1 = line1[0]
    x2, y2 = line1[1]
    x3, y3 = line2[0]
    x4, y4 = line2[1]
    denom = (x1-x2)*(y3-y4) - (y1-y2)*(x3-x4)
    if denom == 0:
        return False
    ua = ((x1*y2 - y1*x2) * (x3-x4) - (x1-x2) * (x3*y4 - y3*x4)) / denom
    ub = ((x1*y2 - y1*x2) * (y3-y4) - (y1-y2) * (x3*y4 - y3*x4)) / denom
    return 0 <= ua <= 1 and 0 <= ub <= 1


class problem():
    def __init__(self, number):
        json_state = json.load(os.path.join(PROBLEM_FILEDIR, str(number) + ".json"))
        self.number = number
        self.hole = hole(json_state["hole"])
        self.figure = figure(json_state)
        self.initial_pose = pose(self.hole, self.figure)
        self.current_pose = self.initial_pose

class search():
    def __init__(self, problem, neighborhoods, random_nbhd = 0.5):
        """Sets up a search. random_nbhd is the percentage of times a random neighborhood is picked, rather than the best one."""
        self.problem = problem
        self.current_pose = self.problem.initial_pose
        self.best_pose = self.current_pose
        self.valid = self.problem.initial_pose.valid
        self.neighborhoods = {n: (1,2) for n in neighborhoods}
        self.random_nbhd = random_nbhd

    def pick_neighborhood(self):
        """Pick a neighborhood function from the list of neighborhoods."""
        if random.rand() < self.random_nbhd:
            return random.choice(self.problem.neighborhoods.keys())
        best_nbrhd = (None, (0, 1))
        for nbrhd in self.neighborhoods.items():
            if nbrhd[1][0] / nbrhd[1][0] > best_nbrhd[1][0] / best_nbrhd[1][0]:
                best_nbrhd = nbrhd
        self.neighborhoods[best_nbrhd[0]][1][0] += 1
        return best_nbrhd[0]

    def step(self):
        """Takes a step from the current pose."""
        step_fn = self.pick_neighborhood()
        new_pose = step_fn(self.current_pose)
        if new_pose.valid and not self.valid:
            self.valid = True
            self.best_pose = new_pose
            step_fn
            self.neighborhoods[step_fn][1] += 1
        elif new_pose.valid:
            if new_pose.dislikes < self.best_pose.dislikes:
                self.best_pose = new_pose
                self.neighborhoods[step_fn][1] += 1
        elif new_pose.dislikes < self.best_pose.dislikes:
            self.best_pose = new_pose
            self.neighborhoods[step_fn][1] += 1

def main():
    """Main function."""
    for i in range(1, 78):
        if any([i in x for x in os.listdir(SOLUTION_FILEDIR)]):
            continue
        problem = problem(i)
        search(problem, {})