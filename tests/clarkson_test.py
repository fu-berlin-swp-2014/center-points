import unittest
import math

import numpy as np

from centerpoints.clarkson import ClarksonAlgo


class TestLibrary(unittest.TestCase):
    def setUp(self):
        n_points = 1000
        for i in range(n_points):
            pass

    @staticmethod
    def random_sphere_points(n_points, dim):
        assert dim == 3

        # @see http://en.wikipedia.org/wiki/Spherical_coordinate_system
        r = 1
        theta = np.random.rand(n_points) * 2 * math.pi
        phi = np.random.rand(n_points) * 2 * math.pi

        x = r * np.sin(theta) * np.cos(phi)
        y = r * np.sin(theta) * np.sin(phi)
        z = r * np.cos(theta)

        return np.column_stack((x, y, z))

    def test_clarkson(self):
        points = self.random_sphere_points(100, 3)

        a = ClarksonAlgo()
        cpt = a.centerpoint(points)
        cpt2 = a.algo4(points)
        print(cpt, cpt2)

        # for p in points:
        #
        #     if not abs(p[0]**2 + p[1]**2 + p[2]**2 - 1) <= 1e-10:
        #         pass
