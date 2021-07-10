#!/usr/bin/env python3
# plot_barrier.py

# %% imports
import torch
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import cm

from aray.objectives import loss_barrier
# def loss_barrier(edges: List[Edge], hole: torch.tensor, current: torch.tensor, gamma: float) -> torch.tensor:

# %%
x_values = np.linspace(0, 7, 100)
y_values = np.linspace(0, 7, 100)
hole = torch.tensor([[1, 2], [4, 6], [6, 5]])
gamma = 0.1

loss_barrier([], hole, torch.tensor([[1,2.]]), gamma)

# %%
d = lambda x, y: loss_barrier([], hole, torch.tensor([[x, y]]), gamma)
matrix = torch.tensor([[d(x, y) for x in x_values] for y in y_values])
matrix

# %%
fig, ax = plt.subplots()

# color scale from matrix min to matrix max
cmap = cm.get_cmap('viridis')
norm = mpl.colors.Normalize(vmin=matrix.min().item(), vmax=matrix.max().item())

# plot matrix with matshow and colorbar
pcm = ax.pcolormesh(x_values, y_values, matrix, cmap=cmap, norm=norm)
fig.colorbar(pcm, ax=ax)

# plot line segment from hole[0] to hole[1], [1] to [2], [2] to [0]
ax.plot([hole[0, 0].item(), hole[1, 0].item()], [hole[0, 1].item(), hole[1, 1].item()], 'k:')
ax.plot([hole[1, 0].item(), hole[2, 0].item()], [hole[1, 1].item(), hole[2, 1].item()], 'k:')
ax.plot([hole[2, 0].item(), hole[0, 0].item()], [hole[2, 1].item(), hole[0, 1].item()], 'k:')


# %%
x_values = np.linspace(0, 7, 100)
y_values = np.linspace(0, 7, 100)
hole = torch.tensor([[1, 2], [4, 6], [6, 5]])
gamma = 1.0

loss_barrier([], hole, torch.tensor([[1,2.]]), gamma)

# %%
d = lambda x, y: loss_barrier([], hole, torch.tensor([[x, y]]), gamma)
matrix = torch.tensor([[d(x, y) for x in x_values] for y in y_values])
matrix

# %%
fig, ax = plt.subplots()

# color scale from matrix min to matrix max
cmap = cm.get_cmap('viridis')
norm = mpl.colors.Normalize(vmin=matrix.min().item(), vmax=matrix.max().item())

# plot matrix with matshow and colorbar
pcm = ax.pcolormesh(x_values, y_values, matrix, cmap=cmap, norm=norm)
fig.colorbar(pcm, ax=ax)

# plot line segment from hole[0] to hole[1], [1] to [2], [2] to [0]
ax.plot([hole[0, 0].item(), hole[1, 0].item()], [hole[0, 1].item(), hole[1, 1].item()], 'k:')
ax.plot([hole[1, 0].item(), hole[2, 0].item()], [hole[1, 1].item(), hole[2, 1].item()], 'k:')
ax.plot([hole[2, 0].item(), hole[0, 0].item()], [hole[2, 1].item(), hole[0, 1].item()], 'k:')


# %%
x_values = np.linspace(0, 7, 100)
y_values = np.linspace(0, 7, 100)
hole = torch.tensor([[1, 1], [3, 5], [6, 1], [6, 6], [1, 6]])
gamma = 2.0
edges = [[0, 1]]

loss_barrier(edges, hole, torch.tensor([[1.5,2.], [1.5,2.5]]), gamma)

# %%
d = lambda x, y: loss_barrier(edges, hole, torch.tensor([[1.5,4.],[x, y]]), gamma)
matrix = torch.tensor([[d(x, y) for x in x_values] for y in y_values])
matrix

# %%
fig, ax = plt.subplots()

# color scale from matrix min to matrix max
cmap = cm.get_cmap('viridis')
norm = mpl.colors.Normalize(vmin=matrix.min().item(), vmax=matrix.max().item())

# plot matrix with matshow and colorbar
pcm = ax.pcolormesh(x_values, y_values, matrix, cmap=cmap, norm=norm)
fig.colorbar(pcm, ax=ax)

# plot line segment from each successive hole point, wrapping around
for i in range(len(hole) - 1):
    ax.plot([hole[i, 0].item(), hole[i + 1, 0].item()], [hole[i, 1].item(), hole[i + 1, 1].item()], 'k:')

# plot the anchor point of current in red
ax.plot([1.5], [4], 'ro')