import unittest
import math
import numpy as np

class TestLibrary(unittest.TestCase):
    def setUp(self):
        n_points = 1000
        for i in range(n_points):
            pass

    @staticmethod
    def random_sphere_points(n_points, dim):
        angle = np.random.rand(n_points, dim-1) * 2*math.pi
        x = np.sin(angle[:, 0])
        y = np.cos(angle[:, 0])
        z = np.sin(angle[:, 1])
        return np.dstack([x, y, z])

    def test_clarkson(self):
        points = self.random_sphere_points(100, 3)
        for p in points:
            if not abs(p[0]**2 + p[1]**2 + p[2]**2 - 1) <= 1e-10:
                pass

