import unittest
import math


import numpy as np

from centerpoints.iterated_tverberg import IteratedTverberg
from centerpoints.helpers import uniform_sphere_points


class TestLibrary(unittest.TestCase):
    def setUp(self):
        n_points = 1000
        for i in range(n_points):
            pass

    def test_tverberg(self):
        points = uniform_sphere_points(50000, 3)

        a = IteratedTverberg()
        cpt = a.centerpoint(points)
        print(cpt)

        # for p in points:
        #
        #     if not abs(p[0]**2 + p[1]**2 + p[2]**2 - 1) <= 1e-10:
        #         pass

    def test_tverberg_1d(self):
        points = np.arange(2000)
        np.random.shuffle(points)
        points.shape = (2000, 1)

        c = IteratedTverberg()
        cpt = c.centerpoint(points)
        print(cpt)

    def test_tverberg_2d(self):
        points = []
        for i in range(-100, 100):
            points.append([i, 2 * i])

        c = IteratedTverberg()
        cpt = c.centerpoint(points)
        print(cpt)
