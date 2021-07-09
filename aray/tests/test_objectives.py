#!/usr/bin/env python3
# test_objectives.py

import unittest
import torch

from aray.objectives import dist


class TestDistance(unittest.TestCase):
    def test_dist_dims(self):
        a = torch.tensor([0, 0], dtype=torch.float)
        b = torch.tensor([1, 1], dtype=torch.float)
        self.assertEqual(dist(a, b).tolist(), 2.)
        a = torch.tensor([[0, 0]], dtype=torch.float)
        b = torch.tensor([[1, 1]], dtype=torch.float)
        self.assertEqual(dist(a, b).tolist(), [2.])
        a = torch.tensor([[[0, 0]]], dtype=torch.float)
        b = torch.tensor([[[1, 1]]], dtype=torch.float)
        self.assertEqual(dist(a, b).tolist(), [[2.]])

    def test_dist_math(self):
        a = torch.Tensor([0, 0])
        b = torch.Tensor([3, 4])
        self.assertEqual(dist(a, b).tolist(), 25.)



if __name__ == '__main__':
    unittest.main()