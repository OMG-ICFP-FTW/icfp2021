#!/usr/bin/env python3

# %%

import os
import json
import matplotlib.pyplot as plt

from aray.problem import Problem, Pose, BASE_PATH

problem = Problem.get(4)
fname = os.path.join(BASE_PATH, 'candidates', '4-9172-cpsolver.json')
with open(fname, 'r') as f:
    pose = Pose.from_json(json.load(f))
print(pose)
print(problem)