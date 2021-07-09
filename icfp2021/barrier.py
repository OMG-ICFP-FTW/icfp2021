#!/usr/bin/env python3

# %%
import numpy as np
import matplotlib.pyplot as plt

# plot -log(x) for x in [0, 1]
x = np.linspace(1e-6, 1, 10000)
for a in [0.1, 0.5, 1, 2, 5, 10]:
    plt.plot(x, -a * np.log(x), label=f'$a={a}$')
plt.xlim(0, 1)
plt.ylim(0, 10)
plt.xlabel('$x$')
plt.ylabel('$-a \log(x)$')
plt.legend()
# draw a horizontal line at y = 0.5
plt.plot([0, 1], [0.5, 0.5], 'k--')
# %%
