import itertools
import json
import math
import matplotlib.pyplot as plt
import os
import time

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

def inside_hole(hole, point):
    """Given a list of (x,y) pairs in hole, calculate the winding number of the vectors from point to those pairs in hole."""
    x, y = point
    sum_theta = 0
    for h in hole + [hole[0]]:
        x1, y1 = h
        sum_theta += math.atan2(y1-y, x1-x)
    return abs(sum_theta) < math.pi / 2

def ring_intersection(hole, ca, cb, ed_a, ed_b):
    """Given two ring centers ca and cb, and two radii ranges ed_a and ed_b, find the integer points that are in both rings.
    
    Begins by finding the quadrilateral of the 'possible region', and then looks for integer points within that region."""
    d = dist(ca, cb)
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
        guesses = [g for g in guesses if ed_a[0] <= dist(g, ca) <= ed_a[1] and ed_b[0] <= dist(g, cb) <= ed_b[1] and inside_hole(hole, g)]
        plt.scatter(pxs, pys)
        if len(guesses) > 0:
            return guesses
    return []

p = json.load(open("problems/15.json"))
print(inside_hole(p["hole"], (29, 19)))

edge_dists = []
for edge in p["figure"]["edges"]:
    edge_dist = dist(p["figure"]["vertices"][edge[0]], p["figure"]["vertices"][edge[1]])
    edge_dists.append([edge_dist * (1 - p["epsilon"]/1000000.0), edge_dist * (1 + p["epsilon"]/1000000.0)])

def check_edge_dists(guess_pos, edge_dists, p):
    guess_ed = [dist(guess_pos[a],guess_pos[b]) if guess_pos[a][0] != -1 and guess_pos[b][0] != -1 else -1 for (a, b) in p["figure"]["edges"]]
    return any([g < ed[0] or g > ed[1] if g > 0 else False for g, ed in zip(guess_ed, edge_dists)])

best_sol = 9999999
things_to_try = itertools.permutations(range(len(p["figure"]["vertices"])))
lenph = len(p["hole"])
tried = 0
# plot_hole(p["hole"])
# plot_figure(p["figure"]["edges"], p["figure"]["vertices"])
# plt.show()
for guess in things_to_try:
    guess_pos = [p["hole"][g] if g < lenph else [-1, -1] for g in guess]
    if check_edge_dists(guess_pos, edge_dists, p):
        continue
    tried += 1
    # plot_hole(p["hole"])
    # plot_figure(p["figure"]["edges"], guess_pos)
    guesses = ring_intersection(p["hole"], guess_pos[2], guess_pos[3], edge_dists[4], edge_dists[5])  # These shouldn't be hardcoded :(
    if len(guesses) > 0:
        guess_pos[-1] = guesses[0]
        if check_edge_dists(guess_pos, edge_dists, p):
            continue
        plot_figure(p["figure"]["edges"], guess_pos)
        json.dump({"vertices": guess_pos},open(os.path.join("solutions",f"15-0-{time.time()}.json"),'w'))
        plt.show()
        break
    # plt.show()