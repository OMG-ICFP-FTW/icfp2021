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

# %%
def loss_stretch(problem, solution):