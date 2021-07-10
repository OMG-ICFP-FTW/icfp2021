import sys
import json
import matplotlib.pyplot as plt

def plot_hole(hole):
    xs, ys = zip(*hole)
    xs = list(xs)
    ys = list(ys)
    xs.append(xs[0])
    ys.append(ys[0])
    plt.plot(xs,ys,c='b')

def plot_figure(edges, vertices):
    for edge in edges:
        a = vertices[edge[0]]
        b = vertices[edge[1]]
        xs, ys = zip(a,b)
        plt.plot(xs, ys,c='r')

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("display_solution.py <PROBLEM FILE> <SOLUTION FILE>")
        exit(1)

    problem = json.load(open(sys.argv[1]))
    solution = json.load(open(sys.argv[2]))
    plot_hole(problem["hole"])
    plot_figure(problem["figure"]["edges"], solution["vertices"])
    plt.show()

