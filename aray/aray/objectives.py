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


def outside(p1: torch.tensor, p2: torch.tensor, p0: torch.tensor):
    """ Get the distance from p0 to the closest point on the line p1-p2, positive if outside """
    assert p1.shape == (2, ) and p2.shape == (2, ) and p0.shape == (2, )
    x0, y0 = p0
    x1, y1 = p1
    x2, y2 = p2
    return torch.abs((x2 - x1) * (y1 - y0) - (x1 - x0) * (y2 - y1)) / ((x2 - x1)**2 + (y2 - y1)**2)**0.5


def loss_stretch(edges: List[Edge], original: torch.tensor, current: torch.tensor, epsilon: int):
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


def loss_dislikes(hole: torch.tensor, current: torch.tensor, temperature: float):
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


# def loss_barrier(edges: List[Edge], hole: torch.tensor, current: torch.tensor, gamma: float):
#     '''
#     ### Barrier:

#     The solution must lie entirely within our (possibly concave) hole.  We enforce this with barrier functions.

#     We have two sets of barrier functions: barriers from the hole to the solution and barriers from the solution to the hole.

#     The objective assumes every point is valid.  To enforce this, we occasionally check if there are invalid points, and then abort if found.

#     For each point in the body, we add barrier loss for every edge that is < 1 distance away.

#     Distance is calculated as normal euclidean distance `dist(a, b) = ((a[0] - b[0])**2 + (a[1] - b[1])**2)**0.5`.

#     This barrier loss is logarithmic: `barrier = - gamma * log(dist)`, with `gamma` controlling the sharpness.

#     (TODO: should try inverse barrier as well, `barrier = gamma / dist`)
#     '''
#     assert hole.shape[-1] == 2, f'{hole.shape}'
#     assert current.shape[-1] == 2, f'{current.shape}'
#     assert len(hole.shape) == 2, f'{hole.shape}'
#     assert len(current.shape) == 2, f'{current.shape}'
#     assert gamma >= 0, f'{gamma}'
#     assert isinstance(gamma, float), f'{gamma}'
#     assert len(edges) > 0, f'{edges}'

#     for i, (v1, v2) in enumerate(edges):

#         d = dist(hole[v1], hole[v2])
#         if d < 1:
#             return gamma * torch.log(d)
    # assert
