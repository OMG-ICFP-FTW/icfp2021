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
problem_number = 42
r = requests.get("https://poses.live/api/problems/" + str(problem_number), headers=headers)
problem = r.json()
problem

# %% print out the length of all the edges
for i in range(len(problem['figure']['edges'])):
    edge = problem['figure']['edges'][i]
    a = problem['figure']['vertices'][edge[0]]
    b = problem['figure']['vertices'][edge[1]]
    print(f"{i}: {dist(a, b)}")


# %% post a solution
solution = {
    "vertices": None,
}

# %%
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

# plot the solution in blue
if solution['vertices'] is not None:
    for i in range(len(edges)):
        v1 = solution['vertices'][edges[i][0]]
        v2 = solution['vertices'][edges[i][1]]
        plt.plot([v1[0], v2[0]], [v1[1], v2[1]], "b-")

# flip the y-axis
plt.gca().invert_yaxis()



# %%
# Calculate all the distances between original and final points
def dist(a, b):
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2

def ratio(a1, b1, a2, b2):
    return abs((dist(a2, b2) / dist(a1, b1)) - 1) * 1_000_000

# get all the ratios for all the edges as a list
def get_ratios(problem, solution):
    ratios = []
    for edge in problem['figure']['edges']:
        r = ratio(problem['figure']['vertices'][edge[0]], problem['figure']['vertices'][edge[1]], solution['vertices'][edge[0]], solution['vertices'][edge[1]])
        ratios.append(r)
    return ratios

max_ratio = max(get_ratios(problem, solution))
assert max_ratio < problem['epsilon'], f'{max_ratio} > {problem["epsilon"]}'
max_ratio

# %%
import itertools
best = None
best_ratio = None
possible_points = problem['hole']
number_of_points = len(figure['vertices'])

# try all possible orderings of the points, drawing with replacement
for ordering in itertools.product(possible_points, repeat=number_of_points):
    candidate = {'vertices': list(ordering)}
    this_ratio = max(get_ratios(problem, candidate))
    if best is None or this_ratio < best_ratio:
        best = candidate
        best_ratio = this_ratio
print(best_ratio)
print(best)
solution = best

# %%
r = requests.post(
    "https://poses.live/api/problems/" + str(problem_number) + "/solutions",
    json=solution,
    headers=headers
)
r.raise_for_status()
r.text

# %%
problem

# %%
import time
skip = 1, 11, 12, 13, 16, 17, 18, 22, 23, 27
for i in range(1,60):
    time.sleep(1)
    if i in skip:
        continue
    print('problem', i)
    r = requests.get("https://poses.live/api/problems/" + str(i), headers=headers)
    problem = r.json()
    figure = problem["figure"]
    vertices = figure["vertices"]  # list of (x, y) pairs
    edges = figure["edges"]  # list of (vertex, vertex) pairs

    if len(vertices) > 10 or len(problem['hole']) > 10:
        print('too big, skipping')
        continue
    print('problem', problem)

    best = None
    best_ratio = None
    possible_points = problem['hole']
    number_of_points = len(figure['vertices'])

    # try all possible orderings of the points, drawing with replacement
    for ordering in itertools.product(possible_points, repeat=number_of_points):
        candidate = {'vertices': list(ordering)}
        this_ratio = max(get_ratios(problem, candidate))
        if best is None or this_ratio < best_ratio:
            best = candidate
            best_ratio = this_ratio
    print(best_ratio)
    print(best)
    solution = best

    # check if the ratio is within the tolerance
    if best_ratio < problem['epsilon']:
        print('submitting', i)
        # Submit the solution
        r = requests.post(
            "https://poses.live/api/problems/" + str(i) + "/solutions",
            json=solution,
            headers=headers
        )
        try:
            r.raise_for_status()
        except Exception as exc:
            print('There was a problem: %s' % (exc))
            continue
        print(r.text)
        continue
    else:
        print('failed to find', i)
        continue