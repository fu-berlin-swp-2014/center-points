import unittest
import math

import numpy as np

from centerpoints.clarkson import ClarksonAlgo
from centerpoints.helpers import random_sphere_points


class TestLibrary(unittest.TestCase):
    def setUp(self):
        n_points = 1000
        for i in range(n_points):
            pass


    def test_clarkson(self):
        points = random_sphere_points(100, 3)

        cpt = ClarksonAlgo().centerpoint(points)
        cpt2 = ClarksonAlgo(True).centerpoint(points)
        print(cpt, cpt2)

        # for p in points:
        #
        #     if not abs(p[0]**2 + p[1]**2 + p[2]**2 - 1) <= 1e-10:
        #         pass

    def test_clarkson_1d(self):
        points = np.arange(100)
        points.shape = (100, 1)

        cpt = ClarksonAlgo().centerpoint(points)
        cpt2 = ClarksonAlgo(True).centerpoint(points)
        print(cpt, cpt2)

    def test_clarkson_2d(self):
        points = []
        for i in range(-100, 100):
            points.append([i, 2 * i])

        cpt = ClarksonAlgo().centerpoint(points)
        cpt2 = ClarksonAlgo(True).centerpoint(points)
        print(cpt, cpt2)
