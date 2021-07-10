#!/usr/bin/env python3
# test_problem.py

# %%
import unittest
from dataclasses import asdict
from aray.problem import Problem, Figure


class TestProblem(unittest.TestCase):
    def test_problem_get(self):
        problem = asdict(Problem.get(1))
        self.assertIsInstance(problem, dict)
        correct = {"hole": [[45, 80], [35, 95], [5, 95], [35, 50], [5, 5], [35, 5], [95, 95], [65, 95], [55, 80]], "epsilon": 150000, "figure": {"edges": [[2, 5], [5, 4], [4, 1], [1, 0], [0, 8], [8, 3], [3, 7], [7, 11], [11, 13], [13, 12], [12, 18], [18, 19], [19, 14], [14, 15], [15, 17], [17, 16], [16, 10], [10, 6], [
            6, 2], [8, 12], [7, 9], [9, 3], [8, 9], [9, 12], [13, 9], [9, 11], [4, 8], [12, 14], [5, 10], [10, 15]], "vertices": [[20, 30], [20, 40], [30, 95], [40, 15], [40, 35], [40, 65], [40, 95], [45, 5], [45, 25], [50, 15], [50, 70], [55, 5], [55, 25], [60, 15], [60, 35], [60, 65], [60, 95], [70, 95], [80, 30], [80, 40]]}}
        self.assertDictEqual(problem, correct)

    def test_problem_subfield(self):
        problem = Problem.get(1)
        self.assertIsInstance(problem.hole, list)
        self.assertIsInstance(problem.epsilon, int)
        self.assertIsInstance(problem.figure, Figure)


if __name__ == '__main__':
    unittest.main()
