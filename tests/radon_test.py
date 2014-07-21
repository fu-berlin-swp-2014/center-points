import unittest
import math

import numpy as np

from centerpoints.iterated_radon import IteratedRadon
from centerpoints.helpers import random_sphere_points


class TestLibrary(unittest.TestCase):
    def setUp(self):
        n_points = 1000
        for i in range(n_points):
            pass


    def test_radon(self):
        points = random_sphere_points(100, 3)

        cpt = IteratedRadon().centerpoint(points)
        cpt2 = IteratedRadon(True).centerpoint(points)
        print(cpt, cpt2)

        # for p in points:
        #
        #     if not abs(p[0]**2 + p[1]**2 + p[2]**2 - 1) <= 1e-10:
        #         pass

    def test_radon_1d(self):
        points = np.arange(100)
        points.shape = (100, 1)

        cpt = IteratedRadon().centerpoint(points)
        cpt2 = IteratedRadon(True).centerpoint(points)
        print(cpt, cpt2)

    def test_radon_2d(self):
        points = []
        for i in range(-100, 100):
            points.append([i, 2 * i])

        cpt = IteratedRadon().centerpoint(points)
        cpt2 = IteratedRadon(True).centerpoint(points)
        print(cpt, cpt2)
