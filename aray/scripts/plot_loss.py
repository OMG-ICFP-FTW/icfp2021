#!/usr/bin/env python3

# %% imports
import torch
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict

from aray.problem import Problem
from aray.objectives import loss_stretch, loss_dislikes, loss_barrier

# %%
# def loss_stretch(edges: List[Edge], original: torch.tensor, current: torch.tensor, epsilon: int) -> torch.tensor:
# def loss_dislikes(hole: torch.tensor, current: torch.tensor, temperature: float) -> torch.tensor:
# def loss_barrier(edges: List[Edge], hole: torch.tensor, current: torch.tensor, gamma: float) -> torch.tensor:
temperature = 1.0
gamma = 1.0


def loss(problem: Problem, vertices: torch.tensor) -> Dict[str, torch.tensor]:
    edges = problem.figure.edges
    hole = torch.tensor(problem.hole, dtype=torch.float)
    original = torch.tensor(problem.figure.vertices, dtype=torch.float)
    return {
        'stretch': loss_stretch(edges, original, vertices, problem.epsilon),
        'dislikes': loss_dislikes(hole, vertices, temperature),
        'barrier': loss_barrier(edges, hole, vertices, gamma),
    }


problem = Problem.get(11)
initial = torch.tensor(problem.figure.vertices, dtype=torch.float)
initial += torch.randn_like(initial) * 10  # jitter
initial *= 1e-2  # make it super tiny
initial += torch.tensor([[5, 8]])

# requires grad for learnable variable
vertices = torch.tensor(initial, requires_grad=True)
loss(problem, vertices)

# %% make a torch optimizer for our variable
optimizer = torch.optim.SGD([vertices], lr=0.001)
# %% plot the vertices on top of the hole and the original position
def plot(vertices: torch.tensor):
    fig, ax = plt.subplots()
    # plot hole first
    hole = problem.hole
    for i in range(len(hole)):
        j = (i + 1) % len(hole)
        ax.plot([hole[i][0], hole[j][0]], [hole[i][1], hole[j][1]], 'k-')
    # plot the original pose
    original = problem.figure.vertices
    for v1, v2 in problem.figure.edges:
        ax.plot([original[v1][0], original[v2][0]], [original[v1][1], original[v2][1]], 'b-')
    # plot the new pose in red
    current = vertices.detach().numpy()
    for v1, v2 in problem.figure.edges:
        ax.plot([current[v1][0], current[v2][0]], [current[v1][1], current[v2][1]], 'r-')

    # flip y axis
    ax.invert_yaxis()

    # show the figure
    plt.show()

plot(vertices)

# %% 
for i in range(10000):
    # assert there are no nans in vertices or loss
    assert not torch.isnan(vertices).any(), f'step {i}'
    optimizer.zero_grad()
    l = loss(problem, vertices)
    sum(l.values()).backward()
    optimizer.step()
    if i % 100 == 0:
        print(l)
        print(vertices)
        plot(vertices)

# %%
vertices
# %%
loss(problem, vertices)

