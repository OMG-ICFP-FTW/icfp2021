#!/usr/bin/env python3

# %% imports
import torch
import numpy as np

# %% problem 42
problem = {
    "hole": [
        [0, 5],
        [6, 0],
        [34, 0],
        [36, 8],
        [43, 15],
        [48, 0],
        [56, 2],
        [56, 42],
        [52, 49],
        [45, 53],
        [37, 52],
        [28, 53],
        [19, 52],
        [7, 53],
        [11, 40],
        [0, 43],
    ],
    "epsilon": 50378,
    "figure": {
        "edges": [
            [0, 1],
            [0, 2],
            [1, 3],
            [1, 5],
            [2, 4],
            [2, 6],
            [3, 4],
            [3, 5],
            [4, 6],
            [5, 6],
        ],
        "vertices": [[26, 21], [48, 10], [25, 44], [25, 7], [10, 25], [0, 20], [10, 0]],
    },
}
hole = problem["hole"]
epsilon = problem["epsilon"]
figure = problem["figure"]
edges = problem["figure"]["edges"]
vertices = problem["figure"]["vertices"]

# %% learnable solution var
solution = torch.tensor(vertices, dtype=torch.float64, requires_grad=True)
solution

# %% optimizer
optimizer = torch.optim.Adam([solution])

# %% function to compute the loss
def loss(solution):
    # first component of the loss is checking if each point violates the hole
    # for 
    pass


# %% optimization loop
for i in range(1000):
    optimizer.zero_grad()
    loss = torch.tensor(0.0, dtype=torch.float64)



# %%
def get_dist(p1, p2, p0):
    """ Get the distance from p0 to the closest point on the line p1-p2 """
    # p1 = torch.tensor(p1, dtype=torch.float)
    # p2 = torch.tensor(p2, dtype=torch.float)
    # p0 = torch.tensor(p0, dtype=torch.float)
    # first assert points are all shape == (2, )
    assert p1.shape == (2, ) and p2.shape == (2, ) and p0.shape == (2, )
    # assert tensors are all type float
    assert p1.dtype == torch.float and p2.dtype == torch.float and p0.dtype == torch.float
    x10 = p1[0] - p0[0]
    y10 = p1[1] - p0[1]
    x21 = p2[0] - p1[0]
    y21 = p2[1] - p1[1]
    dist = (x21*y10 - x10*y21) / torch.sqrt(torch.square(x21) + torch.square(y21))
    return dist

a = torch.tensor([0., 0.], dtype=torch.float)
b = torch.tensor([2., 2.], dtype=torch.float)
c = torch.tensor([0., 1.], dtype=torch.float)
get_dist(a, b, c)

# %% plot the lines and the points
import matplotlib.pyplot as plt

# plot a-b and point c
plt.plot([a[0], b[0]], [a[1], b[1]], color="black")
plt.plot(c[0], c[1], "o", color="black")

# %% plot the points in hole, connecting back to the first point
hole_points = hole + [hole[0]]
plt.plot([p[0] for p in hole_points], [p[1] for p in hole_points], "k-")

# %% get the distance from the point (30, 30) to all of the edges in the hole
p = torch.tensor([30, 30], dtype=torch.float)

# iterate over the pairs of points in the hole
for i in range(len(hole)):
    p1 = torch.tensor(hole[i], dtype=torch.float)
    p2 = torch.tensor(hole[(i + 1) % len(hole)], dtype=torch.float)
    dist = get_dist(p1, p2, p)
    print(f"{i}: {dist}, {p1} {p2}")
    # plot the line between the points
    plt.plot([p1[0], p2[0]], [p1[1], p2[1]], color="blue" if i == 4 else "black")
plt.plot(p[0], p[1], "o", color="red")