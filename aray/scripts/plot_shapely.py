#!/usr/bin/env python3
# plot_shapely.py

# %%
import matplotlib.pyplot as plt

from aray.problem import Problem

from shapely.geometry import Polygon, Point, LineString, GeometryCollection, LinearRing, MultiPoint

# %%
def get_points(hole):
    poly = Polygon(hole)
    min_x, min_y, max_x, max_y = poly.bounds
    points = []
    for x in range(int(min_x), int(max_x) + 1):
        for y in range(int(min_y), int(max_y) + 1):
            if poly.intersects(Point(x, y)):
                points.append((x, y))
    return points

def get_forbidden(hole, delta):
    poly = Polygon(hole)
    forbidden = []
    for a in points:
        b = (a[0] + delta[0], a[1] + delta[1])
        if b not in points:
            continue
        ab = LineString((a, b))
        if poly.contains(ab) or ab.within(poly):
            continue
        elif poly.exterior.crosses(ab):
            forbidden.append((a, b))
        elif poly.touches(ab) and not poly.exterior.contains(ab):
            forbidden.append((a, b))
    return forbidden

fig, ax = plt.subplots()
problem = Problem.get(14)
problem.plot(fig, ax)


points = get_points(problem.hole)
xs = [p[0] for p in points]
ys = [p[1] for p in points]
ax.scatter(xs, ys)

forbidden = get_forbidden(problem.hole, (2, 0))
for a, b in forbidden:
    ax.plot((a[0], b[0]), (a[1], b[1]))
forbidden


# %%

edge = ((10,10), (12,9))
ax.plot((edge[0][0], edge[1][0]), (edge[0][1], edge[1][1]))

# %%
poly = Polygon(problem.hole)
mp = MultiPoint(edge)
repr(mp.convex_hull)

ls = LineString(edge)

poly.crosses(ls)
