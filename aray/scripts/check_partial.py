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

from tqdm.notebook import trange

for _ in trange(10):  # big outer loop
    # match files like '{problem_number}-{score_number}-{string}.json'
    FILENAME_REGEX = re.compile(r'(\d+)-(\d+)-cpsolver.json')

    solutions = os.path.join(BASE_PATH, 'candidates')
    scores = {}  # map from problem_number -> score_number
    poses = {}  # map from problem_number -> Pose
    problems = {}  # map from problem_number -> Problem
    for file in glob(os.path.join(solutions, '*')):
        # check if the filename matches
        match = FILENAME_REGEX.match(os.path.basename(file))
        if match:
            problem_number = int(match.group(1))
            score = int(match.group(2))
            with open(file) as f:
                data = json.load(f)
            pose = Pose.from_json(data)
            problem = Problem.get(problem_number)

            partial = Partial.from_problem(problem)
            solution = pose.vertices
            indexes = list(range(len(solution)))  # order to be compared
            random.shuffle(indexes)

            assert len(indexes) == len(solution), f'{indexes} {solution}'
            for i in indexes:
                v = solution[i]
                unplaced_points = partial.get_unplaced_points()
                assert i in unplaced_points, f'{i} {unplaced_points}'
                placement = partial.get_placement_for_point(i)
                assert v in placement, f'{v} {placement}'
                partial.place_point(i, v)
            
            assert len(partial.get_unplaced_points()) == 0, f'{partial}'