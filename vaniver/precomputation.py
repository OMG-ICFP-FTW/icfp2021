import json
import os
import matplotlib.pyplot as plt

problems = {}
filedir = "problems"
for filename in os.listdir(filedir):
    with open(os.path.join(filedir,filename)) as file:
        problems[int(filename.split(".")[0])] = json.loads(file.read())

data = {}
names = ["num_holes","num_figures","epsilon","min_x","min_y","max_x","max_y","delta_x","delta_y"]
for name in names:
    data[name] = []
zeroes = 0
for p in problems.values():
    data["num_holes"].append(len(p["hole"]))
    data["num_figures"].append(len(p["figure"]["vertices"]))
    data["epsilon"].append(p["epsilon"])
    if p["epsilon"] == 0:
        zeroes += 1
    xs = []
    ys = []
    for h in p["hole"]:
        xs.append(h[0])
        ys.append(h[1])
    data["min_x"].append(min(xs))
    data["max_x"].append(max(xs))
    data["delta_x"].append(data["max_x"][-1]-data["min_x"][-1])
    data["min_y"].append(min(ys))
    data["max_y"].append(max(ys))
    data["delta_y"].append(data["max_y"][-1]-data["min_y"][-1])

plt.scatter(data["num_holes"], data["num_figures"])
plt.xlabel("hole vertices")
plt.ylabel("figure vertices")
plt.show()

for name in names:
    plt.hist(data[name])
    plt.title(name)
    plt.show()

print("Number of zeroes:", zeroes)