#!/usr/bin/env python3
# objectives.py - objective functions for our gradient descent optimization


'''
Stretch:
^^^^^^^^

"Stretch" is the ratio of a resulting edge with its original length.

The problem specifies a maximum stretch, and there is no benefit to having a stretch which is smaller than the maximum. 

The ratio to stay within is ``epsilon/1_000_000`` where ``epsilon`` is given for the problem.

We compute this for edge ``a, b`` with ``stretch = max(abs(d(a', b') / d(a, b) - 1) * 1e6 - epsilon), 0)``, where

- ``a`` and ``b`` are the original points
- ``a'`` and ``b'`` are the new points
- ``d(a, b)`` is the squared distance function ``d(a, b) = (a[0] - b[0])**2 + (a[1] - b[1])**2``
'''

# %% imports
from typing import List
import torch

from aray.problem import Edge


# %% distance function
def dist(a: torch.tensor, b: torch.tensor) -> torch.tensor:
    ''' Squared distance function for points a and b. '''
    # assert a and b have same shape, and last dim is 2
    assert a.shape == b.shape, f'a and b have different shapes: {a.shape} and {b.shape}'
    assert a.shape[-1] == 2, f'a and b have last dim != 2: {a.shape}'
    result = (a[..., 0] - b[..., 0])**2 + (a[..., 1] - b[..., 1])**2
    # assert result matches shape of a and b, without the last dim
    assert result.shape == a.shape[:-1], f'dist(a, b) {result.shape} a {a.shape}'
    return result


# %%
def loss_stretch(edges: List[Edge], original: torch.tensor, current: torch.tensor, epsilon: int):
    ''' Calculate the total stretch loss for a problem '''
    # assert original and current have 2 dims, same shape, and second dim is 2
    assert original.shape == current.shape, f'{original.shape} vs {current.shape}'
    assert original.shape[-1] == 2, f'last dim != 2: {original.shape}'
    assert len(original.shape) == 2, f'{original.shape}'

    ratio = torch.empty(len(edges), dtype=torch.float)
    for i, (v1, v2) in enumerate(edges):
        d_orig = dist(original[v1], original[v2])
        d_curr = dist(current[v1], current[v2])
        ratio[i] = d_curr / d_orig
    
    stretch = torch.max(torch.abs(ratio - 1) * 1e6 - epsilon, torch.zeros_like(ratio))
    return torch.sum(stretch)