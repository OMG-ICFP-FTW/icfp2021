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
    result = (a[..., 0] - b[..., 0])**2 + (a[..., 1] - b[..., 1])**2
    # assert result matches shape of a and b, without the last dim
    assert result.shape == a.shape[:-1], f'{result.shape} vs {a.shape}'
    return result


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
    assert D.shape == (len(hole), len(current)), f'{D.shape} vs {len(hole),len(current)}'
    W = torch.softmax(-D / temperature, dim=1)
    assert D.shape == W.shape, f'{D.shape} vs {W.shape}'
    return torch.sum(D * W)
