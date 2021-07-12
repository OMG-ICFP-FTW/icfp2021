#!/usr/bin/env python3
# parse the score table

# %%
import os
import json
from bs4 import BeautifulSoup

# get the directory this file is in
dir_path = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(dir_path, 'score_table.html')) as f:
    html = f.read()
html = html.replace('❌', '')
# parse the html
soup = BeautifulSoup(html, 'html.parser')
# find all the table
tables = soup.find_all('table')
# get the first table
table = tables[0]
# get the rows of the table as lists
rows = table.find_all('tr')
# process the rows into strings of data
data = []
for row in rows:
    data.append([None if val.text == '' else int(val.text) for val in row.find_all('td')])
data
# process into a dict of dicts
scores = {}
for row in data:
    if row == []:
        continue
    problem_number = row[0]
    our_score = row[1]
    best_score = row[2]
    assert problem_number not in scores
    scores[problem_number] = {
        'problem_number': problem_number,
        'our_score': our_score,
        'best_score': best_score,
    }
# write to json file
with open('/tmp/scores.json', 'w') as f:
    json.dump(scores, f)

# %%
# get all the problem numbers where our score == best score
best_scores = []
for i in range(1, 131):
    if scores[i]['our_score'] == scores[i]['best_score']:
        best_scores.append(i)
best_scores

# %%
# get the list of problem_numbers that our score is currently missing
# missing_scores = []
# for i in range(1, 131):
#     if i == 104:
#         continue
#     if scores[i]['our_score'] == None:
#         missing_scores.append(i)
# missing_scores

# # %%
# forbiddens_list = '''
# /tmp/104-forbidden2.json
# /tmp/108-forbidden2.json
# /tmp/109-forbidden2.json
# /tmp/10-forbidden2.json
# /tmp/110-forbidden2.json
# /tmp/113-forbidden2.json
# /tmp/119-forbidden2.json
# /tmp/11-forbidden2.json
# /tmp/120-forbidden2.json
# /tmp/123-forbidden2.json
# /tmp/127-forbidden2.json
# /tmp/12-forbidden2.json
# /tmp/130-forbidden2.json
# /tmp/132-forbidden2.json
# /tmp/13-forbidden2.json
# /tmp/14-forbidden2.json
# /tmp/15-forbidden2.json
# /tmp/16-forbidden2.json
# /tmp/17-forbidden2.json
# /tmp/18-forbidden2.json
# /tmp/19-forbidden2.json
# /tmp/1-forbidden2.json
# /tmp/20-forbidden2.json
# /tmp/21-forbidden2.json
# /tmp/22-forbidden2.json
# /tmp/23-forbidden2.json
# /tmp/24-forbidden2.json
# /tmp/25-forbidden2.json
# /tmp/26-forbidden2.json
# /tmp/27-forbidden2.json
# /tmp/28-forbidden2.json
# /tmp/29-forbidden2.json
# /tmp/2-forbidden2.json
# /tmp/30-forbidden2.json
# /tmp/31-forbidden2.json
# /tmp/32-forbidden2.json
# /tmp/33-forbidden2.json
# /tmp/34-forbidden2.json
# /tmp/35-forbidden2.json
# /tmp/36-forbidden2.json
# /tmp/37-forbidden2.json
# /tmp/38-forbidden2.json
# /tmp/39-forbidden2.json
# /tmp/3-forbidden2.json
# /tmp/40-forbidden2.json
# /tmp/41-forbidden2.json
# /tmp/42-forbidden2.json
# /tmp/43-forbidden2.json
# /tmp/44-forbidden2.json
# /tmp/45-forbidden2.json
# /tmp/46-forbidden2.json
# /tmp/47-forbidden2.json
# /tmp/48-forbidden2.json
# /tmp/49-forbidden2.json
# /tmp/4-forbidden2.json
# /tmp/50-forbidden2.json
# /tmp/51-forbidden2.json
# /tmp/52-forbidden2.json
# /tmp/53-forbidden2.json
# /tmp/54-forbidden2.json
# /tmp/55-forbidden2.json
# /tmp/56-forbidden2.json
# /tmp/57-forbidden2.json
# /tmp/58-forbidden2.json
# /tmp/59-forbidden2.json
# /tmp/5-forbidden2.json
# /tmp/60-forbidden2.json
# /tmp/61-forbidden2.json
# /tmp/63-forbidden2.json
# /tmp/66-forbidden2.json
# /tmp/67-forbidden2.json
# /tmp/69-forbidden2.json
# /tmp/6-forbidden2.json
# /tmp/70-forbidden2.json
# /tmp/73-forbidden2.json
# /tmp/77-forbidden2.json
# /tmp/7-forbidden2.json
# /tmp/81-forbidden2.json
# /tmp/84-forbidden2.json
# /tmp/86-forbidden2.json
# /tmp/88-forbidden2.json
# /tmp/89-forbidden2.json
# /tmp/8-forbidden2.json
# /tmp/91-forbidden2.json
# /tmp/92-forbidden2.json
# /tmp/94-forbidden2.json
# '''.strip().split()
# forbidden_numbers = [int(x[5:].split('-')[0]) for x in forbiddens_list]
# forbidden_numbers

# # %%
# ns = sorted(i for i in forbidden_numbers if i in missing_scores)
# ' '.join(str(i) for i in ns)

# # %%
# # bash command to run these
# for x in ns:
#     print(f'python gosh_dangit_its_them_ortools_boys_again/edgy.py {x} --timeout 10000.0 &')
