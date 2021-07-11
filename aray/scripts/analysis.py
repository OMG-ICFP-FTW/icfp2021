#!/usr/bin/env python3

# %%
import re
from glob import glob
import os
import json
import numpy as np
import matplotlib.pyplot as plt

from aray.problem import Problem, BASE_PATH, Pose

# %%
numbers = list(range(1, 133))
problems = {i: Problem.get(i) for i in numbers}

# %%
solutions = {}  # map from problem number to best solution we have
# match files like '{problem_number}-{dislikes}-{string}.json'
FILENAME_REGEX = re.compile(r'(\d+)-(\d+)-(.+).json')
for file in glob(os.path.join(os.path.join(BASE_PATH, 'solutions'), '*')):
    # check if the filename matches
    match = FILENAME_REGEX.match(os.path.basename(file))
    if match:
        problem_number = int(match.group(1))
        dislikes = int(match.group(2))
        with open(file) as f:
            data = json.load(f)
        solution = Pose.from_json(data, dislikes)
        # add it to our solutions map if it's better than what we have
        if problem_number not in solutions or solutions[problem_number].dislikes < dislikes:
            solutions[problem_number] = solution

# %%
unsolved = {i: problem for i, problem in problems.items() if i not in solutions}

# %%
num_edges = [len(problems[i].edges) for i in numbers]
num_vertices = [len(problems[i].vertices) for i in numbers]

plt.scatter(num_edges, num_vertices)
plt.xlabel('Number of edges')
plt.ylabel('Number of vertices')
plt.title('Number of edges vs. number of vertices for each problem')

# %%
plt.title('Cumulative unsolved with at most this many vertices')
plt.xlabel('Number of vertices')
plt.ylabel('Number of unsolved with at most X vertices')

vertices = {i: len(unsolved[i].vertices) for i in unsolved.keys()}
xs = sorted(set(vertices.values()))
ys = [sum(1 for i in vertices.keys() if vertices[i] <= x) for x in xs]

# plot with only a small dot
plt.scatter(xs, ys, s=1)

# add 10s grid to x axis
plt.xticks(range(0, max(xs), 10))

# %%
# print out unsolved problem numbers with at most 25 vertices
pairs = []
for i in unsolved.keys():
    if len(unsolved[i].vertices) <= 25:
        pairs.append((i, len(unsolved[i].vertices)))

# sort by number of vertices
pairs.sort(key=lambda pair: pair[1])
for i, v in pairs:
    print(f'Problem {i}: {v} vertices')