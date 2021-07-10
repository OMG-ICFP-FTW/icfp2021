#!/usr/bin/env python3
# plot_dislikes.py

# %% imports
import torch
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import cm

from aray.objectives import loss_dislikes

# def loss_dislikes(hole: torch.tensor, current: torch.tensor, temperature: float) -> torch.tensor:

# %%
x_values = np.linspace(0, 7, 100)
y_values = np.linspace(0, 7, 100)
hole = torch.tensor([[1, 2], [4, 6], [6, 5]])
temperature = 0.1

loss_dislikes(hole, torch.tensor([[1, 2], [1.1, 2.1], [4, 6], [6, 5]]) + .01, temperature)


# %%
d = lambda x, y: loss_dislikes(hole, torch.tensor([[1.5,2.5],[4.5, 6.5],[6.5,5.5], [x, y]]), temperature)
matrix = torch.tensor([[d(x, y) for x in x_values] for y in y_values])
matrix


# %%
fig, ax = plt.subplots()

# color scale from matrix min to matrix max
cmap = cm.get_cmap('viridis_r')
norm = mpl.colors.Normalize(vmin=matrix.min().item(), vmax=matrix.max().item())

# plot matrix with matshow and colorbar
pcm = ax.pcolormesh(x_values, y_values, matrix, cmap=cmap, norm=norm)
fig.colorbar(pcm, ax=ax)

# plot line segment from hole[0] to hole[1], [1] to [2], [2] to [0]
ax.plot([hole[0, 0].item(), hole[1, 0].item()], [hole[0, 1].item(), hole[1, 1].item()], 'k:')
ax.plot([hole[1, 0].item(), hole[2, 0].item()], [hole[1, 1].item(), hole[2, 1].item()], 'k:')
ax.plot([hole[2, 0].item(), hole[0, 0].item()], [hole[2, 1].item(), hole[0, 1].item()], 'k:')