#!/usr/bin/env python3

# %%
import numpy as np
import matplotlib.pyplot as plt

from aray.problem import Problem

# %%

problems = {i: Problem.get(i) for i in range(1, 133)}