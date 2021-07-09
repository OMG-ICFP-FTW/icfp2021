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
import torch

# %% distance function


def dist(a: torch.tensor, b: torch.tensor) -> torch.tensor:
    '''
    Squared distance function for points a and b.
    '''
    # assert a and b have same shape, and last dim is 2
    assert a.shape == b.shape, f'a and b have different shapes: {a.shape} and {b.shape}'
    assert a.shape[-1] == 2, f'a and b have last dim != 2: {a.shape}'
    result = (a[..., 0] - b[..., 0])**2 + (a[..., 1] - b[..., 1])**2
    # assert result matches shape of a and b, without the last dim
    assert result.shape == a.shape[:-1], f'dist(a, b) {result.shape} a {a.shape}'
    return result


# %%
# def loss_stretch(problem, solution):
