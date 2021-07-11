import json
import math
import traceback
from time import sleep

from ortools.sat.python import cp_model
# from shapely.geometry import Polygon, Point, LineString

import argparse
import multiprocessing
import os
import requests
import logging
from enum import Enum

# import matplotlib.pyplot as plt
# plt.style.use('seaborn-whitegrid')

def problem_url(problem_id):
    return 'http://poses.live/api/problems/{}'.format(problem_id)

def get_problem(problem_id):
    headers = {'Authorization': 'Bearer {}'.format(os.environ['STEEZYKEY'])}
    logging.info(f'Fetching problem {problem_id}')
    r = requests.get(problem_url(problem_id), headers=headers)
    return r.json()

def submit_url(problem_id):
    return 'http://poses.live/api/problems/{}/solutions'.format(problem_id)

def submit_pose(problem_id, data):
    headers = {'Authorization': 'Bearer {}'.format(os.environ['STEEZYKEY'])}
    r = requests.post(submit_url(problem_id), headers=headers, data=data)
    return r

def dsq(v1, v2):
    return math.pow(v2[0] - v1[0], 2) + math.pow(v2[1] - v1[1], 2)

class PointOrientation(Enum):
    LEFT = 1
    RIGHT = 2
    COLINEAR = 3

def Area2(a, b, c):
    return (b[0] - a[0])*(c[1] - a[1]) - (c[0] - a[0])*(b[1] - a[1])

# Mad propz to the geniuses at:
# https://www.geeksforgeeks.org/check-if-two-given-line-segments-intersect/
def orientation(a, b, c):
    a = Area2(a, b, c)
    if a > 0:
        return PointOrientation.LEFT
    if a < 0:
        return PointOrientation.RIGHT
    return PointOrientation.COLINEAR # a == 0

def test_line_intersection(line1, line2):
    p1, p2 = line1
    p3, p4 = line2

    o1 = orientation(p1, p2, p3)
    o2 = orientation(p1, p2, p4)
    o3 = orientation(p3, p4, p1)
    o4 = orientation(p3, p4, p2)

    # We are actually OK with a point being on the boundary
    if o1 == PointOrientation.COLINEAR:
        return False
    if o2 == PointOrientation.COLINEAR:
        return False
    if o3 == PointOrientation.COLINEAR:
        return False
    if o4 == PointOrientation.COLINEAR:
        return False

    if o1 != o2 and o3 != o4:
        return True

    return False

def test_segment_intersects_hole(segment, hole):
    for i, h1 in enumerate(hole):
        j = (i+1)%len(hole)
        h2 = hole[j]
        if test_line_intersection(segment, (h1, h2)):
            return True
    return False

def compute_dislikes(hole, pose):
    total_dislike = 0
    for hole_pt in hole:
        total_dislike += min([dsq(hole_pt, pose_pt) for pose_pt in pose])
    return total_dislike

def bounding_box(pj):
    minx =  200000000
    miny =  200000000
    maxx = -200000000
    maxy = -200000000

    for (x,y) in pj['hole']:
        if x < minx:
            minx = x
        if y < miny:
            miny = y
        if x > maxx:
            maxx = x
        if y > maxy:
            maxy = y

    return minx, miny, maxx, maxy

class VarArraySolutionPrinter(cp_model.CpSolverSolutionCallback):
    """Print intermediate solutions."""

    def __init__(self, pose_vertices, hole):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self._pose_vertices = pose_vertices
        self._hole = hole
        self._best_solution = None
        self._least_dislike = None

    def on_solution_callback(self):
        try:
            solution = []
            for i, v in self._pose_vertices.items():
                solution.append([self.Value(v[0]), self.Value(v[1])])

            d = compute_dislikes(self._hole, solution)
            if self._least_dislike is None or d < self._least_dislike:
                self._least_dislike = d
                self._best_solution = solution
                logging.info(f"Dislike: {self._least_dislike}")
                logging.info(json.dumps({
                    "vertices": self._best_solution,
                }))
        except Exception as e:
            logging.warning(e)
            traceback.print_exc()
            sleep(10)
            raise

    def best_solution(self):
        return self._best_solution, self._least_dislike

# !!! MAGIC ALERT !!!
#
# CERTIFIED JOE MAGIC
class Brainfart:
    def __init__(self, problem, max_deterministic_time=None, num_search_workers=None):
        self.hole = problem["hole"]
        self.figure_edges = problem["figure"]["edges"]
        self.figure_vertices = problem["figure"]["vertices"]
        self.epsilon = problem["epsilon"]

        self._max_deterministic_time = max_deterministic_time
        self._num_search_workers = num_search_workers

        # calculated in run()
        self.allowed_positions = []

    def run(self):
        model = cp_model.CpModel()

        # Hole Bounding box
        hole_min_x = min([p[0] for p in self.hole])
        hole_max_x = max([p[0] for p in self.hole])
        hole_min_y = min([p[1] for p in self.hole])
        hole_max_y = max([p[1] for p in self.hole])
        logging.info(f"Hole x={hole_min_x}:{hole_max_x} y={hole_min_y}:{hole_max_y}")

        # Create model variables for each pose vertex
        pose_vertices = {}
        for i, v in enumerate(self.figure_vertices):
            pose_vertices[i] = (
                model.NewIntVar(hole_min_x, hole_max_x, f'{i}_x'),
                model.NewIntVar(hole_min_y, hole_max_y, f'{i}_y')
            )

        sh_hole = Polygon(self.hole)
        sh_hole_linestring = sh_hole.exterior
        for x in range(hole_min_x, hole_max_x + 1):
            for y in range(hole_min_y, hole_max_y + 1):
                if sh_hole.contains(Point(x, y)) or sh_hole_linestring.distance(Point(x, y)) < 1e-8:
                    self.allowed_positions.append((x, y))

        logging.info(
            f"Hole possible locations {len(self.allowed_positions)} / {(hole_max_x - hole_min_x) * (hole_max_y - hole_min_y)}")

        # Create a map of all possible starting and ending x,y for each edge
        logging.info(f"Total edges {len(self.figure_edges)}")
        for i, edge in enumerate(self.figure_edges):
            v1 = self.figure_vertices[edge[0]]
            v2 = self.figure_vertices[edge[1]]
            sq_distance = dsq(v1, v2)  # math.pow(v2[0] - v1[0], 2) + math.pow(v2[1] - v1[1], 2)

            # calculates about 1M allowed lines per minute
            allowed_assignments = []
            for p1 in self.allowed_positions:
                for p2 in self.allowed_positions:
                    new_sq_distance = dsq(p1, p2)  # math.pow(p2[0] - p1[0], 2) + math.pow(p2[1] - p1[1], 2)

                    r = abs(new_sq_distance / sq_distance - 1)

                    if r <= self.epsilon / 1000000:
                        # check if the line collides with the hole
                        # XXX myenik hax
                        # sh_edge = LineString([p1, p2])
                        # intersection = sh_edge.intersection(sh_hole_linestring)
                        # if isinstance(intersection, Point):
                        #     # logging.info(f"Intersection is single point {intersection} relative to {p1} and {p2}")
                        #     # logging.info(intersection.distance(Point(p1)))
                        #     # logging.info(intersection.distance(Point(p2)))
                        #     if intersection.distance(Point(p1)) > 1e-8 and intersection.distance(Point(p2)) > 1e-8:
                        #         continue
                        # else:
                        #     # logging.debug(f"Skip collision {p1} -> {p2} = {sh_edge.intersection(sh_hole_linestring)}")
                        #     continue
                        # allowed_assignments.append((p1[0], p1[1], p2[0], p2[1]))
                        segment = (p1, p2)
                        if test_segment_intersects_hole(segment, self.hole):
                            continue
                        allowed_assignments.append((p1[0], p1[1], p2[0], p2[1]))

            model.AddAllowedAssignments([
                pose_vertices[edge[0]][0],
                pose_vertices[edge[0]][1],
                pose_vertices[edge[1]][0],
                pose_vertices[edge[1]][1]
            ], allowed_assignments)

            logging.info(
                f"{i}: ({edge[0]}) {v1} -> ({edge[1]}) {v2} with distance {sq_distance} has {len(allowed_assignments)} allowed assignments")

        solver = cp_model.CpSolver()

        if self._max_deterministic_time is not None:
            solver.parameters.max_deterministic_time = self._max_deterministic_time

        if self._num_search_workers is not None:
            solver.parameters.num_search_workers = self._num_search_workers

        solution_printer = VarArraySolutionPrinter(pose_vertices, self.hole)
        status = solver.SearchForAllSolutions(model, solution_printer)
        # status = solver.Solve(model, solution_callback=solution_printer)

        print('Status = %s' % solver.StatusName(status))
        print(f'Best solution found: {solution_printer.best_solution()}')
        return solution_printer.best_solution()

    # def visualize(self, pose):
    #     plt.axis('equal')

    #     x = [i[0] for i in self.hole]
    #     y = [i[1] for i in self.hole]
    #     plt.fill(x, y, facecolor='none', edgecolor='purple', linewidth=3)

    #     x = [i[0] for i in self.allowed_positions]
    #     y = [i[1] for i in self.allowed_positions]
    #     plt.plot(x, y, 'o', color='black')

    #     x = [i[0] for i in self.figure_vertices]
    #     y = [i[1] for i in self.figure_vertices]
    #     plt.plot(x, y, 'o', color='blue')

    #     if pose is not None:
    #         x = [i[0] for i in pose]
    #         y = [i[1] for i in pose]
    #         plt.fill(x, y, facecolor='lightsalmon', edgecolor='orangered', linewidth=3)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Gang shit')
    parser.add_argument('-s', '--submit',
                        help='Submit solutions to API (otherwise print and save) CURRENTLY NOT WORKING',
                        action='store_true',
    )
    parser.add_argument('-v', '--verbose',
                        help='Enable debug logs',
                        action='store_true',
    )
    parser.add_argument('-l', '--logfile',
                        help='File to store logs',
                        type=str,
                        default='/tmp/solver_log.txt',
    )
    parser.add_argument('-j', '--json_dir',
                        help='Place to dump json solutions',
                        type=str,
                        default='/tmp',
    )
    parser.add_argument('-p', '--problem',
                        help='Problem to solve (otherwise solves all)',
                        type=int,
                        default=0,
    )
    parser.add_argument('-d', '--deadline',
                        help='Deadline in seconds for the solver to spend on each problem',
                        type=int,
                        default=60,
    )
    parser.add_argument('-t', '--threads',
                        help='Number of threads to use for solver',
                        type=int,
                        default=multiprocessing.cpu_count(),
    )
    args = parser.parse_args()

    # Set up logging
    if args.verbose:
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s [%(levelname)s] %(message)s",
            handlers=[
                logging.FileHandler(args.logfile),
                logging.StreamHandler()
            ]
        )
    else:
        logging.basicConfig(
            level=logging.WARNING,
            format="%(asctime)s [%(levelname)s] %(message)s",
            handlers=[
                logging.FileHandler(args.logfile),
                logging.StreamHandler()
            ]
        )

    logging.info('New run with args:')
    logging.info(' '.join(f'{k}={v}' for k, v in vars(args).items()))

    # Get solver settings
    settings = {
        "max_deterministic_time": args.deadline,
        # "num_search_workers": args.threads,
        "num_search_workers": 1, # Apparently SearchForAllSolutions doesn't support running in parallel...
    }

    # Do one problem or all
    problems = []
    if args.problem == 0:
        problems = list(range(1, 10))
    else:
        problems = [args.problem]

    # Fetch problem jsons
    #
    # TODO(myenik): Cache these for faster development
    problem_jsons = list(map(get_problem, problems))

    # Sort problems by bounding box area
    sorted_problems = []
    for problem, pj in zip(problems, problem_jsons):
        minx, miny, maxx, maxy = bounding_box(pj)
        size = (maxx-minx)*(maxy-miny)
        sorted_problems.append((problem, pj, size))
    sorted_problems = sorted(sorted_problems, key=lambda x: x[2])
    for problem, pj, bb_size in sorted_problems:
        logging.info(f'Problem {problem} estimated complexity factor {bb_size}')

    summary = {}
    for problem, pj, bb_size in sorted_problems:
        logging.info(f'Solving problem {problem}')
        brainfarter = Brainfart(pj, **settings)
        pose, dislikes = brainfarter.run()

        if pose == None:
            logging.info(f'FAILED! - ayy lmao')
            summary[problem] = ':('
        else:
            logging.info(f'SOLVED! - {problem} has {dislikes} dislikes with solution {pose}')
            summary[problem] = dislikes
            solution_json = {"vertices": pose}
            if args.submit:
                logging.info(submit_pose(problem, solution_json).text)
            else:
                solution_path = os.path.join(args.json_dir, f'{problem}.solution')
                logging.info(f'Saving solution for problem {problem} to {solution_path}')
                with open(solution_path, 'w') as f:
                    f.write(json.dumps(solution_json))

    logging.info('SUMMARY')
    for p, s in summary.items():
        logging.info(f'{p:3} => {s:10}')
