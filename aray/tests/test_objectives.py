#!/usr/bin/env python3
# test_objectives.py

import unittest
import torch

from aray.objectives import dist, near, loss_stretch, loss_dislikes, loss_barrier


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
        a = torch.tensor([0, 0])
        b = torch.tensor([3, 4])
        self.assertEqual(dist(a, b).tolist(), 25.)


class TestNear(unittest.TestCase):
    def test_on_segment(self):
        a = torch.tensor([0, 0])
        b = torch.tensor([2, 2])
        p = torch.tensor([1, 1])
        self.assertEqual(near(a, b, p).tolist(), 0.0)
        self.assertEqual(near(a, b, a).tolist(), 0.0)
        self.assertEqual(near(a, b, b).tolist(), 0.0)

    def test_horizontal(self):
        a = torch.tensor([0, 0])
        b = torch.tensor([2, 0])
        p = torch.tensor([0, 1])
        self.assertEqual(near(a, b, p).tolist(), 1.0)
        self.assertEqual(near(a, b, b + p).tolist(), 1.0)
        self.assertAlmostEqual(near(a, b, 2 * b + p).tolist(), 5.0**0.5)
        self.assertAlmostEqual(near(a, b, -b).tolist(), 2.0)
        self.assertAlmostEqual(near(a, b, -b - p).tolist(), 5.0**0.5)


class TestStretch(unittest.TestCase):
    def test_basic_bigger(self):
        edges = [[0, 1]]
        original = torch.tensor([[0, 0], [0, 10]], dtype=torch.float)
        current = torch.tensor([[0, 0], [0, 11]], dtype=torch.float)
        epsilon = 0
        loss = loss_stretch(edges, original, current, epsilon)
        correct = abs((11**2 / 10**2) - 1) * 1e6
        self.assertAlmostEqual(loss.tolist(), correct, places=1)

    def test_basic_smaller(self):
        edges = [[0, 1]]
        original = torch.tensor([[0, 0], [0, 2]], dtype=torch.float)
        current = torch.tensor([[0, 0], [0, 1]], dtype=torch.float)
        epsilon = 0
        loss = loss_stretch(edges, original, current, epsilon)
        correct = abs((1**2 / 2**2) - 1) * 1e6
        self.assertAlmostEqual(loss.tolist(), correct, places=1)

    def test_basic_epsilon(self):
        edges = [[0, 1]]
        original = torch.tensor([[0, 0], [0, 2]], dtype=torch.float)
        current = torch.tensor([[0, 0], [0, 1]], dtype=torch.float)
        epsilon = 500_000
        loss = loss_stretch(edges, original, current, epsilon)
        correct = abs((1**2 / 2**2) - 1) * 1e6 - epsilon
        self.assertAlmostEqual(loss.tolist(), correct, places=1)

    def test_basic_zero(self):
        edges = [[0, 1]]
        original = torch.tensor([[0, 0], [0, 2]], dtype=torch.float)
        current = torch.tensor([[0, 0], [0, 1]], dtype=torch.float)
        epsilon = 1_000_000
        loss = loss_stretch(edges, original, current, epsilon)
        correct = 0.0
        self.assertAlmostEqual(loss.tolist(), correct, places=1)


class TestDislikes(unittest.TestCase):
    def test_dislike_zero(self):
        hole = torch.tensor([[0, 0]], dtype=torch.float)
        current = torch.tensor([[0, 0]], dtype=torch.float)
        temperature = 1.0
        loss = loss_dislikes(hole, current, temperature)
        correct = 0.0
        self.assertAlmostEqual(loss.tolist(), correct, places=7)

    def test_dislike_one(self):
        hole = torch.tensor([[0, 0]], dtype=torch.float)
        current = torch.tensor([[0, 1]], dtype=torch.float)
        temperature = 1.0
        loss = loss_dislikes(hole, current, temperature)
        correct = 1.0
        self.assertAlmostEqual(loss.tolist(), correct, places=7)

    def test_dislike_multiple(self):
        hole = torch.tensor([[0, 0]], dtype=torch.float)
        current = torch.tensor([[0, 1], [0, 2]], dtype=torch.float)
        temperature = 1.0
        loss = loss_dislikes(hole, current, temperature)
        correct_dist = torch.tensor([1, 4], dtype=torch.float)
        correct_weight = torch.nn.functional.softmax(-correct_dist, dim=0)
        correct = (correct_weight * correct_dist).sum()
        self.assertAlmostEqual(loss.tolist(), correct, places=7)

    def test_dislike_far(self):
        hole = torch.tensor([[0, 0], [100, 100]], dtype=torch.float)
        current = torch.tensor([[99, 100], [0, 1]], dtype=torch.float)
        temperature = 1.0
        loss = loss_dislikes(hole, current, temperature)
        correct = 2.0
        self.assertAlmostEqual(loss.tolist(), correct, places=7)


class TestBarrier(unittest.TestCase):
    def test_basic(self):
        pass


if __name__ == '__main__':
    unittest.main()