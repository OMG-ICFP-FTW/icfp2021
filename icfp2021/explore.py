#!/usr/bin/env python3

"""
Poses can be submit through the web portal at https://poses.live. After registering on that portal, teams can
submit poses either directly through the upload form provided in the web portal, or through an HTTP API
at the same domain.
In order to use the HTTP API, teams must first obtain their API token through the web portal. You can
find this your team’s page. Each request must then include this token in an Authorization header:
Authorization: Bearer $YOUR_API_TOKEN
The HTTP API supports the following methods:
GET /api/hello Says hello to your team. This can be used to verify that your API token works.
GET /api/problems/$PROBLEM_ID Retrieves the JSON encoding of the specified problem.
POST /api/problems/$PROBLEM_ID/solutions Submit a pose. The request body must contain a JSON
encoding of a pose. Returns a pose ID.
"""

# %% imports
import requests

# %%
TEAM_NAME = "OMG ICFP FTW"
YOUR_API_TOKEN = "b5d3e724-0d12-4926-b223-e9cd180c3003"
headers = {"Authorization": "Bearer " + YOUR_API_TOKEN}

# %% say hello
r = requests.get("https://poses.live/api/hello", headers=headers)
assert r.json() == {"hello": TEAM_NAME}, r.text

# %% get a problem
r = requests.get("https://poses.live/api/problems/1", headers=headers)
problem = r.json()

# %% post a solution
solution = {
    "vertices": [
        [21, 28],
        [31, 28],
        [31, 87],
        [29, 41],
        [44, 43],
        [58, 70],
        [38, 79],
        [32, 31],
        [36, 50],
        [39, 40],
        [66, 77],
        [42, 29],
        [46, 49],
        [49, 38],
        [39, 57],
        [69, 66],
        [41, 70],
        [39, 60],
        [42, 25],
        [40, 35],
    ]
}
r = requests.post(
    "https://poses.live/api/problems/1/solutions", json=solution, headers=headers
)
r.raise_for_status()
r.text


# %% plot all of the line segments on a 2d canvas
import numpy as np
import matplotlib.pyplot as plt

hole = problem["hole"]  # list of (x, y) pairs, in order
# draw all the lines
for i in range(len(hole) - 1):
    x = [hole[i][0], hole[i + 1][0]]
    y = [hole[i][1], hole[i + 1][1]]
    plt.plot(x, y, "k-")
# also connect the first and last points
x = [hole[0][0], hole[-1][0]]
y = [hole[0][1], hole[-1][1]]
plt.plot(x, y, "k-")

figure = problem["figure"]
vertices = figure["vertices"]  # list of (x, y) pairs
edges = figure["edges"]  # list of (vertex, vertex) pairs

# draw all the lines
for i in range(len(edges)):
    v1 = vertices[edges[i][0]]
    v2 = vertices[edges[i][1]]
    plt.plot([v1[0], v2[0]], [v1[1], v2[1]], "r-")

# flip the y-axis
plt.gca().invert_yaxis()
