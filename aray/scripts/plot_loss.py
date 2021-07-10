#!/usr/bin/env python3

# %% imports
import torch
import numpy as np
import matplotlib.pyplot as plt

from aray.problem import Problem
from aray.objectives import loss_stretch, loss_dislikes, loss_barrier

# %%
# def loss_stretch(edges: List[Edge], original: torch.tensor, current: torch.tensor, epsilon: int) -> torch.tensor:
# def loss_dislikes(hole: torch.tensor, current: torch.tensor, temperature: float) -> torch.tensor:
# def loss_barrier(edges: List[Edge], hole: torch.tensor, current: torch.tensor, gamma: float) -> torch.tensor:
temperature = 1.0
gamma = 1.0


def loss(problem: Problem, vertices: torch.tensor) -> torch.tensor:
    edges = problem.figure.edges
    hole = torch.tensor(problem.hole, dtype=torch.float)
    original = torch.tensor(problem.figure.vertices, dtype=torch.float)

    stretch = loss_stretch(edges, original, vertices, problem.epsilon)
    dislikes = loss_dislikes(hole, vertices, temperature)
    barrier = loss_barrier(edges, hole, vertices, gamma)
    print('stretch', stretch)
    print('dislikes', dislikes)
    print('barrier', barrier)


problem = Problem.get(1)
problem.figure


# %%
# this will be our learned variable
vertices = torch.tensor(problem.figure.vertices, dtype=torch.float, requires_grad=True)

loss(problem, vertices)