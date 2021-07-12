#!/usr/bin/env python3

# %%
import requests
import json


API_KEY = "b5d3e724-0d12-4926-b223-e9cd180c3003"
def submit_url(problem_id):
    return f'https://poses.live/api/problems/{problem_id}/solutions'
def submit_solution(problem_id, pose):
    headers = {'Authorization': f'Bearer {API_KEY}'}
    r = requests.post(submit_url(problem_id), headers=headers, json=pose)
    return r
def status_url(problem_id, pose_id):
    return f"https://poses.live/api/problems/{problem_id}/solutions/{pose_id}"
def get_status(problem_id, pose_id):
    headers = {'Authorization': f'Bearer {API_KEY}'}
    r = requests.get(status_url(problem_id, pose_id), headers=headers)
    return r


# %%
from glob import glob
import re

problems_to_ignore = [104, 45]
tablefile = '/tmp/scores.json'
with open(tablefile, 'r') as f:
    table = json.load(f)
table = {int(k): v for k, v in table.items()}

# regex to match the pattern {problem_number}-{score}-cpsolver3.json
# we'll use the problem_number and score so they need to be grouped
regex = re.compile(r'(\d+)-(\d+)-cpsolver3.json')

# search for files that match the pattern in /tmp
for filename in sorted(glob('/tmp/*-cpsolver3.json')):
    match = regex.search(filename)
    if match:
        problem_number = int(match.group(1))
        if problem_number in problems_to_ignore:
            continue
        score = int(match.group(2))
        our_score = table[problem_number]['our_score']
        # print('comparing our score', our_score, 'to', score)
        if our_score is None or our_score > score:
            print('Got a better score, submitting')
            print('Problem', problem_number, 'our score', our_score, 'new score', score)

            # read the file json
            with open(filename, 'r') as f:
                pose = json.load(f)
            # submit the solution
            r = submit_solution(problem_number, pose)
            r.raise_for_status()

# # %%
# # get the problems page
# headers = {'Authorization': f'Bearer {API_KEY}'}
# r = requests.get('https://poses.live/problems', headers=headers)
# r.raise_for_status()
# r.text