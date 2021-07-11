#!/usr/bin/env python3
# check_dislike.py - Check if the dislike scoring matches submitted

# %%
import os
from posix import PRIO_USER
import re
import json
from glob import glob
from aray.problem import BASE_PATH, Problem, Pose
from aray.dislike import dislikes

# match files like '{problem_number}-{score_number}-{string}.json'
FILENAME_REGEX = re.compile(r'(\d+)-(\d+)-(.+).json')

solutions = os.path.join(BASE_PATH, 'solutions')
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
        check = dislikes(problem.hole, pose.vertices)
        assert check == score, f'{i}: {check} != {score}'
        print('checked', match.groups())
