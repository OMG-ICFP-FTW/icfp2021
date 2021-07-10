#!/usr/bin/env python3
# objectives.py - objective functions for our gradient descent optimization


# %% imports
from typing import List
import torch

from aray.problem import Edge


def dist(a: torch.tensor, b: torch.tensor) -> torch.tensor:
    ''' Squared distance function for points a and b. '''
    # assert a and b have same shape, and last dim is 2
    assert a.shape == b.shape, f'{a.shape} vs {b.shape}'
    assert a.shape[-1] == 2, f'{a.shape}'
    return (a[..., 0] - b[..., 0])**2 + (a[..., 1] - b[..., 1])**2


def near(A: torch.tensor, B: torch.tensor, P: torch.tensor):
    """ Get the distance to the nearest point to P on line segment A-B """
    # https://math.stackexchange.com/a/3128850
    assert A.shape == B.shape == P.shape == (2,), \
        f'{A.shape} {B.shape} {P.shape}'
    v = B - A
    u = A - P
    vu = (v * u).sum()
    vv = (v * v).sum()
    t = -vu / vv
    if t < 0:
        closest = A
    elif t > 1:
        closest = B
    else:
        closest = A + t * v
    # convert to floating type and return the norm
    return (closest - P).float().norm()


def loss_stretch(edges: List[Edge], original: torch.tensor, current: torch.tensor, epsilon: int) -> torch.tensor:
    ''' Calculate the total stretch loss for a problem '''
    # assert original and current have 2 dims, same shape, and second dim is 2
    assert original.shape == current.shape, f'{original.shape} vs {current.shape}'
    assert original.shape[-1] == 2, f'{original.shape}'
    assert len(original.shape) == 2, f'{original.shape}'

    ratio = torch.empty(len(edges), dtype=torch.float)
    for i, (v1, v2) in enumerate(edges):
        d_orig = dist(original[v1], original[v2])
        d_curr = dist(current[v1], current[v2])
        ratio[i] = d_curr / d_orig

    stretch = torch.max(torch.abs(ratio - 1) * 1e6 -
                        epsilon, torch.zeros_like(ratio))
    return torch.sum(stretch)


def loss_dislikes(hole: torch.tensor, current: torch.tensor, temperature: float) -> torch.tensor:
    assert hole.shape[-1] == 2, f'{hole.shape}'
    assert current.shape[-1] == 2, f'{current.shape}'
    assert len(hole.shape) == 2, f'{hole.shape}'
    assert len(current.shape) == 2, f'{current.shape}'
    assert temperature >= 0, f'{temperature}'
    assert isinstance(temperature, float), f'{temperature}'

    # compute distance matrix
    Hx = hole[:, None, 0]
    Hy = hole[:, None, 1]
    Vx = current[None, :, 0]
    Vy = current[None, :, 1]
    D = (Hx - Vx)**2 + (Hy - Vy)**2
    assert D.shape == (len(hole), len(current)
                       ), f'{D.shape} vs {len(hole),len(current)}'
    W = torch.softmax(-D / temperature, dim=1)
    assert D.shape == W.shape, f'{D.shape} vs {W.shape}'
    return torch.sum(D * W)


def loss_barrier(edges: List[Edge], hole: torch.tensor, current: torch.tensor, gamma: float) -> torch.tensor:
    assert hole.shape[-1] == 2, f'{hole.shape}'
    assert current.shape[-1] == 2, f'{current.shape}'
    assert len(hole.shape) == 2, f'{hole.shape}'
    assert len(current.shape) == 2, f'{current.shape}'
    assert gamma >= 0, f'{gamma}'

    # make a list of hole edges to match
    hole_edges = list(
        zip(range(len(hole) - 1), range(1, len(hole)))) + [(len(hole) - 1, 0)]

    # compute the distance matrix, first current edges, than hole edges
    curr_matrix = torch.empty(len(edges), len(hole))
    for i, (v1, v2) in enumerate(edges):
        for j, h in enumerate(hole):
            curr_matrix[i, j] = near(current[v1], current[v2], h)

    hole_matrix = torch.empty(len(hole_edges), len(current))
    for i, (v1, v2) in enumerate(hole_edges):
        for j, c in enumerate(current):
            hole_matrix[i, j] = near(hole[v1], hole[v2], c)

    # clamp the distances to be between 1e-8 and gamma
    curr_matrix = torch.clamp(curr_matrix, min=1e-4, max=gamma)
    hole_matrix = torch.clamp(hole_matrix, min=1e-4, max=gamma)

    # convert the distances to losses, pointwise
    curr_loss = -torch.log(curr_matrix / gamma)
    hole_loss = -torch.log(hole_matrix / gamma)

    # sum the losses
    return torch.sum(curr_loss) + torch.sum(hole_loss)