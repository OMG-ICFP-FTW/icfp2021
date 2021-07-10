#!/usr/bin/env python3
# plot_stretch.py


# %% imports
import torch
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import cm

from aray.objectives import loss_stretch
# def loss_stretch(edges: List[Edge], original: torch.tensor, current: torch.tensor, epsilon: int) -> torch.tensor:


# %%
epsilon = 260_000
x_values = np.linspace(0, 7, 100)
y_values = np.linspace(0, 7, 100)
edges = [[0,1]]
original = torch.tensor([[1, 2], [4, 6]])
# loss_stretch(edges, original, torch.tensor([[1,2], [0, 0.]]), epsilon)
d = lambda x, y: loss_stretch(edges, original, torch.tensor([[1, 2], [x, y]]), epsilon)
matrix = torch.tensor([[d(x, y) for x in x_values] for y in y_values])
matrix



# %%
fig, ax = plt.subplots()

# color scale from matrix min to matrix max
cmap = cm.get_cmap('viridis_r')
cmap2 = cm.get_cmap('magma')
norm = mpl.colors.Normalize(vmin=matrix.min().item(), vmax=matrix.max().item())

# plot matrix with matshow and colorbar
pcm = ax.pcolormesh(x_values, y_values, matrix, cmap=cmap, norm=norm)
fig.colorbar(pcm, ax=ax)

# plot line segment from original[0] to original[1]
ax.plot([original[0, 0].item(), original[1, 0].item()], [original[0, 1].item(), original[1, 1].item()], 'k:')

# transparently plot over top of the matrix
# for values where the matrix is 0, plot red, otherwise transparent
# calculate mask by converting the mask to boolean, then inverting, then back to float
mask = (matrix == 0.).float().numpy()
masked = np.ma.masked_array(mask, mask == 0)
pcm2 = ax.pcolormesh(x_values, y_values, masked, cmap=cmap2, norm=norm, alpha=0.5)

# %%
# again but with two reference points
epsilon = 260_000
x_values = np.linspace(0, 7, 100)
y_values = np.linspace(0, 7, 100)
edges = [[0,1], [1, 2]]
original = torch.tensor([[1, 2], [4, 6], [6, 5]])
# loss_stretch(edges, original, torch.tensor([[1,2], [0, 0.]]), epsilon)
d = lambda x, y: loss_stretch(edges, original, torch.tensor([[1, 2], [x, y], [6, 5]]), epsilon)
matrix = torch.tensor([[d(x, y) for x in x_values] for y in y_values])
matrix

# %%
fig, ax = plt.subplots()

# color scale from matrix min to matrix max
cmap = cm.get_cmap('viridis_r')
cmap2 = cm.get_cmap('magma')
norm = mpl.colors.Normalize(vmin=matrix.min().item(), vmax=matrix.max().item())

# plot matrix with matshow and colorbar
pcm = ax.pcolormesh(x_values, y_values, matrix, cmap=cmap, norm=norm)
fig.colorbar(pcm, ax=ax)

# plot line segment from original[0] to original[1] and [1] to original[2]
ax.plot([original[0, 0].item(), original[1, 0].item()], [original[0, 1].item(), original[1, 1].item()], 'k:')
ax.plot([original[1, 0].item(), original[2, 0].item()], [original[1, 1].item(), original[2, 1].item()], 'k:')

# transparently plot over top of the matrix
# for values where the matrix is 0, plot red, otherwise transparent
# calculate mask by converting the mask to boolean, then inverting, then back to float
mask = (matrix == 0.).float().numpy()
masked = np.ma.masked_array(mask, mask == 0)
pcm2 = ax.pcolormesh(x_values, y_values, masked, cmap=cmap2, norm=norm, alpha=0.5)
