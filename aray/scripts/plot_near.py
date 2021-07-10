#!/usr/bin/env python
# plot_near.py

# %% imports
import torch
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import cm

from aray.objectives import near

# %%

A = torch.tensor([1, 2])
B = torch.tensor([4, 6])
x_values = np.linspace(0, 7, 100)
y_values = np.linspace(0, 7, 100)
d = lambda x, y: near(A, B, torch.tensor([x, y]))
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

# plot line segment from A to B
ax.plot([A[0].item(), B[0].item()], [A[1].item(), B[1].item()], 'k:')