import itertools
import json
import math
import os
import random
import sys
import time
from matplotlib.colors import to_hex

from shapely.geometry import Point, Polygon

import matplotlib.pyplot as plt
import numpy as np

PROBLEM_FILEDIR = "problems"
SOLUTION_FILEDIR = "solutions"

sys.setrecursionlimit(1000000)

def vadd(a,b):
    return tuple(map(sum, zip(a,b)))

def vsub(a,b):
    return tuple(map(lambda x: x[0]-x[1], zip(a,b)))

def dist(a, b):
    return (a[0]-b[0])**2 + (a[1]-b[1])**2

def plot_hole(hole):
    xs, ys = zip(*hole)
    xs = list(xs)
    ys = list(ys)
    xs.append(xs[0])
    ys.append(ys[0])
    plt.plot(xs,ys,c='b')

def plot_figure(edges, vertices):
    for edge in edges:
        a = vertices[edge[0]]
        b = vertices[edge[1]]
        xs, ys = zip(a,b)
        plt.plot(xs, ys,c='r')

class problem():
    def __init__(self, number):
        json_state = json.load(open(os.path.join(PROBLEM_FILEDIR, str(number) + ".json")))
        self.number = number
        self.hole = hole(json_state["hole"])
        self.figure = figure(json_state)

class hole():
    def __init__(self, vertices):
        self.vertices = vertices
        self.num_vertices = len(vertices)
        self.vertex_cycle = self.vertices + [self.vertices[0]]
        self.edges = list(zip(self.vertex_cycle[:-1], self.vertex_cycle[1:]))
        self.polygon = Polygon(self.vertices)
        self.inside_set = set()
        self.dist_dict = {}
        xs, ys = zip(*self.vertices)
        for x in range(min(xs), max(xs)+1):
            for y in range(min(ys), max(ys)+1):
                if self.polygon.covers(Point(x,y)):
                    self.inside_set.add((x,y))
                    self.dist_dict[x,y] = [dist((x,y), v) for v in self.vertices]

    def inside(self, point):
        """Checks if point is inside the hole."""
        if isinstance(point, tuple):
            return point in self.inside_set
        return tuple(point) in self.inside_set

    def dislikes(self, positions):
        """Calculates the minimum distance to a vertex in positions for each vertex in the hole."""
        return [min([dist(h, v) for v in positions]) for h in self.vertices]

    def plot(self):
        """Plot the hole."""
        xs, ys = zip(*self.vertex_cycle)
        plt.plot(xs,ys,c='b')

class figure():
    def __init__(self, problem):
        self.edges = [(min(a,b), max(a,b)) for (a,b) in problem["figure"]["edges"]]
        orig_vertices = problem["figure"]["vertices"]
        self.edge_dists = []
        for edge in self.edges:
            edge_dist = dist(orig_vertices[edge[0]], orig_vertices[edge[1]])
            self.edge_dists.append([edge_dist * (1 - problem["epsilon"]/1000000.0), edge_dist * (1 + problem["epsilon"]/1000000.0)])
        self.hole = hole(problem["hole"])
        self.build_adjacency()
        self.num_vertices = len(self.adjacency)

    def build_adjacency(self):
        self.adjacency = {}
        self.adj_dists = {}
        self.adj_vecs = {}
        for edge_ind, edge in enumerate(self.edges):
            if edge[0] in self.adjacency:
                self.adjacency[edge[0]].append(edge[1])
            else:
                self.adjacency[edge[0]] = [edge[1]]
            if edge[1] in self.adjacency:
                self.adjacency[edge[1]].append(edge[0])
            else:
                self.adjacency[edge[1]] = [edge[0]]
            self.adj_dists[edge[0],edge[1]] = self.edge_dists[edge_ind]
            self.adj_dists[edge[1],edge[0]] = self.edge_dists[edge_ind]
            self.adj_vecs[edge[0],edge[1]] = ring_options((0,0), *self.edge_dists[edge_ind])
            self.adj_vecs[edge[1],edge[0]] = self.adj_vecs[edge[0],edge[1]]

    def begin_search(self, best_sol = None):
        """Begin the search for a solution. If passed best_sol, will return the first solution at least that good."""
        initial_candidates = [partial_figure(self, vertex_index, hole_index) for hole_index in range(self.hole.num_vertices) for vertex_index in range(self.num_vertices)]
        result = search(initial_candidates, target=best_sol).run()
                # if v_result is None:
                #     continue
                # if best_sol is not None:
                #     if v_result.sum_dislikes <= best_sol:
                #         return v_result
                # elif best_result is not None and v_result.sum_dislikes < best_result.sum_dislikes:
                #     best_result = v_result
                # elif best_result is None:
                #     best_result = v_result
                # except:
                #     print("Error")
                #     continue
        print("result", result)
        return result


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


def ring_intersection(hole, ca, cb, ed_a, ed_b):
    """Given two ring centers ca and cb, and two squared radii ranges ed_a and ed_b, find the integer points that are in both rings.
    
    Begins by finding the quadrilateral of the 'possible region', and then looks for integer points within that region."""
    d = dist(ca, cb)
    if d == 0:
        return ring_options(ca, max(ed_a[0], ed_b[0]), min(ed_a[1], ed_b[1]))
    plus = []
    minus = []
    for ra, rb in itertools.product(ed_a, ed_b):
        xc = 0.5 * (ca[0] + cb[0]) + (ra - rb)/(2*d) * (cb[0] - ca[0])
        xd = 0.5 * math.sqrt(2 * (ra + rb)/(d) - (ra - rb)**2/(d**2) - 1) * (cb[1] - ca[1])
        yc = 0.5 * (ca[1] + cb[1]) + (ra - rb)/(2*d) * (cb[1] - ca[1])
        yd = 0.5 * math.sqrt(2 * (ra + rb)/(d) - (ra - rb)**2/(d**2) - 1) * (ca[0] - cb[0])
        plus.append((xc+xd, yc+yd))
        minus.append((xc-xd, yc-yd))
    for flip in [plus, minus]:
        pxs, pys = zip(*flip)
        guesses = list(itertools.product(range(math.ceil(min(pxs)), math.floor(max(pxs))+1),
                                        range(math.ceil(min(pys)), math.floor(max(pys))+1)))
        guesses = [g for g in guesses if ed_a[0] <= dist(g, ca) <= ed_a[1] and ed_b[0] <= dist(g, cb) <= ed_b[1] and hole.inside(g)]
        # plt.scatter(pxs, pys)
        if len(guesses) > 0:
            return guesses
    return []


def ring_quad_options(r1, r2):
    """Given two squared radii, yield all integer lattice points in the first quadrant of that ring."""
    for x in range(math.floor(math.sqrt(r2))):
        if x ** 2 > r1:
            min_y1 = 0
        else:
            min_y1 = math.ceil(math.sqrt(r1 - x**2))
        max_y2 = math.floor(math.sqrt(r2 - x**2))
        for y in range(min_y1, max_y2+1):
            yield (x, y)


def ring_options(center, r1, r2):
    """Given a center point and two radii, return a list of all integer lattice points in the ring."""
    quad = ring_quad_options(r1, r2)
    result = set()
    for q in quad:
        if q == (0,0):
            result.add(center)
        else:
            result.add((center[0] + q[0], center[1] + q[1]))
            result.add((center[0] + q[0], center[1] - q[1]))
            result.add((center[0] - q[0], center[1] + q[1]))
            result.add((center[0] - q[0], center[1] - q[1]))
    return list(result)


class partial_figure():
    def __init__(self, figure, vertex_index = None, hole_index = None, to_plot = False):
        self.figure = figure
        self.adjacency = figure.adjacency
        self.adj_dists = figure.adj_dists
        self.vertices = [(None, None) for _ in range(self.figure.num_vertices)]
        self.to_extend = set()
        self.extended = set()
        self.dislikes = [9999999 for _ in range(self.figure.hole.num_vertices)]
        if vertex_index is not None and hole_index is not None:
            self.begin(vertex_index, hole_index)
        self.plot = to_plot

    @property
    def sum_dislikes(self):
        return sum(self.dislikes)

    def valid(self, vertex_index, next_pos):
        """Return True iff the part of the figure relating to making vertex_index next_pos is valid."""
        if not self.figure.hole.inside(next_pos):
            return False
        for edge in self.adjacency[vertex_index]:
            edge_pos = self.vertices[edge]
            if edge_pos[0] is not None:
                dee = dist(next_pos, edge_pos)
                if dee < self.adj_dists[vertex_index, edge][0] or dee > self.adj_dists[vertex_index, edge][1]:
                    return False
                for hedge in self.figure.hole.edges:
                    if check_line_intersection([next_pos, edge_pos], hedge):
                        return False 
        return True

    def valid_full(self):
        """Return True iff the figure is valid. This checks the validity of the whole figure."""
        for vertex in self.vertices:
            if not self.figure.hole.inside(vertex):
                return False
        for edge in self.figure.edges:
            edge0 = tuple(self.vertices[edge[0]])
            edge1 = tuple(self.vertices[edge[1]])
            if edge0 is None or edge1 is None:
                return False
            dee = dist(edge0, edge1)
            if dee < self.adj_dists[(edge[0], edge[1])][0] or dee > self.adj_dists[(edge[0], edge[1])][1]:
                return False
            for hedge in self.figure.hole.edges:
                if check_line_intersection([edge0, edge1], hedge):
                    return False 
        return True

    def begin(self, vertex_index, hole_index):
        """Initialize with the vertex_index at hole_index; return self."""
        self.vertices[vertex_index] = self.figure.hole.vertices[hole_index]
        self.to_extend = self.to_extend.union(self.adjacency[vertex_index])
        self.extended.add(vertex_index)
        self.dislikes = self.figure.hole.dislikes([self.vertices[vertex_index]])
        return self

    def expand(self):
        """Return a list of partial figures or placeholder partial figures, each of which has been extended by the next edge removed from to_extend."""
        if len(self.to_extend) == 0:
            return None
        next_vertex = self.to_extend.pop()
        self.extended.add(next_vertex)
        return_list = []
        for next_pos in self.options(next_vertex):
            if next_pos is not None:
                return_list.append(self.copy_with(next_vertex, next_pos))
        if len(return_list) > 0:
            return return_list
        else:
            return None

    def options(self, next_vertex):
        """Return a list of positions where it would be possible to place the next vertex."""
        # Later I check for other validity; should I just do integer validity here?
        constraints = [(v, self.vertices[v]) for v in self.adjacency[next_vertex] if v in self.extended]
        
        other_ind, other_pos = constraints[0]
        poss = {vadd(other_pos, vec) for vec in self.figure.adj_vecs[next_vertex, other_ind]}
        poss = {v for v in poss if v in self.figure.hole.inside_set}
        for constraint in constraints[1:]:
            other_ind, other_pos = constraint
            [v for v in poss if vsub(other_pos, v) in self.figure.adj_vecs[next_vertex, other_ind]]
        return poss
        # elif len(constraints) == 2:
        #     return ring_intersection(self.figure.hole, constraints[0][0], constraints[1][0], constraints[0][1], constraints[1][1])
        # else:
        #     candidates = None
        #     for cona, conb in itertools.product(constraints):  # TODO: this actually only needs the sorted product?
        #         new_candidates = set(ring_intersection(self.figure.hole, cona[0], conb[0], cona[1], conb[1]))
        #         if candidates is not None:
        #             candidates = candidates.intersection(new_candidates)
        #             if len(candidates) == 0:
        #                 return None
        #         else:
        #             candidates = new_candidates
        #     return list(candidates)


    def copy_with(self, next_vertex, next_pos):
        """Return a copy of self, extended by the next vertex at next_pos."""
        if not self.valid(next_vertex, next_pos):
            return None
        novel = partial_figure(self.figure)
        novel.vertices = self.vertices.copy()
        novel.vertices[next_vertex] = next_pos
        novel.to_extend = self.to_extend.union([v for v in self.adjacency[next_vertex] if v not in self.extended])
        novel.extended = self.extended.copy()
        novel.dislikes = [min(a,b) for a,b in zip(self.dislikes, self.figure.hole.dislikes([next_pos]))]
        if self.plot:
            plot_hole(self.figure.hole.vertices)
            pruned_edges = [e for e in self.figure.edges if e[0] in novel.extended and e[1] in novel.extended]
            plot_figure(pruned_edges, novel.vertices)
            plt.scatter(next_pos[0], next_pos[1], c='m')
            plt.title(str(next_pos))
            plt.show()
        return novel

class search():
    def __init__(self, candidates: list, target=None):
        if len(candidates) == 0:
            return None
        self.num_searched=0
        self.candidates = set(candidates)
        self.finished = None
        self.target = target
    
    def run(self):
        while len(self.candidates) > 0 and (self.finished is None or self.finished.sum_dislikes > self.target):
            self.step()
        return self.finished

    def step(self):
        """step randomly picks a candidate to expand from the set and expands it."""
        # if target is not None and len(candidates[0].to_extend) == 0 and sum(candidates[0].dislikes) <= target:
        #     return candidates[0]
        next_expansion = self.candidates.pop()
        if self.num_searched % 100 == 0:
            print(self.num_searched, len(self.candidates), 
            self.finished.sum_dislikes if self.finished else "-", 
            len(next_expansion.extended), len(next_expansion.to_extend))
        expansion = next_expansion.expand()
        if expansion is not None:
            for e in expansion:
                if e is None:
                    continue
                if len(e.to_extend) == 0 and e.valid_full():
                    if self.finished is None:
                        self.finished = e
                    elif e.sum_dislikes < self.finished.sum_dislikes:
                        self.finished = e
                elif len(e.to_extend) > 0 and e not in self.candidates:
                    self.candidates.add(e)
        self.num_searched += 1


if __name__ == "__main__":
    number = 20
    p = problem(number)
    result = p.figure.begin_search(best_sol=0)
    if result is None:
        print("No solution found")
    else:
        plot_hole(p.figure.hole.vertices)
        plot_figure(p.figure.edges, result.vertices)
        print(result.sum_dislikes)
        print(result.dislikes)
        print(p.figure.hole.dislikes(result.vertices))
        plt.show()
        json.dump({"vertices": result.vertices}, open(os.path.join("solutions",f"{number}-{result.sum_dislikes}-{time.time()}.json"),'w'))