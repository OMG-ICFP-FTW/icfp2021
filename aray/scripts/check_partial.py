#!/usr/bin/env python3
# check_partial.py - check out our partial execution

# %%

import os
import re
import json
import random
import matplotlib.pyplot as plt
from glob import glob
from aray.partial import Partial
from aray.problem import BASE_PATH, Problem, Pose
from aray.types import Point

# match files like '{problem_number}-{score_number}-{string}.json'
FILENAME_REGEX = re.compile(r'(\d+)-(\d+)-(.+).json')

solutions = os.path.join(BASE_PATH, 'solutions')
poses = {}  # map from problem_number -> Pose
problems = {}  # map from problem_number -> Problem
for file in glob(os.path.join(solutions, '*')):
    # check if the filename matches
    match = FILENAME_REGEX.match(os.path.basename(file))
    if match:
        problem_number = int(match.group(1))
        score_number = int(match.group(2))
        with open(file) as f:
            data = json.load(f)
        poses[problem_number] = Pose.from_json(data)
        problems[problem_number] = Problem.get(problem_number)

for problem_number, problem in problems.items():
    print("Problem Number:", problem_number)
    partial = Partial.from_problem(problem)
    solution = poses[problem_number].vertices
    indexes = list(range(len(solution)))  # order to be compared
    # shuffle the indexes to avoid bias
    random.shuffle(indexes)

    # fig, ax = plt.subplots(figsize=(10, 10))
    # ps = list(partial.placement)
    # ax.scatter([p.x for p in ps], [p.y for p in ps])
    # plt.show()
    # assert Point(20, 0) in partial.placement

    assert len(indexes) == len(solution), f'{indexes} {solution}'
    for i in indexes:
        v = solution[i]
        unplaced_points = partial.get_unplaced_points()
        assert i in unplaced_points, f'{i} {unplaced_points}'
        placements = partial.get_placements_for_point(i)
        assert v in placements, f'{v} {placements}'
        partial.place_point(i, v)
    
    assert len(partial.get_unplaced_points()) == 0, f'{partial}'