import unittest

import numpy as np

import centerpoints.data_set as data_set


class TestDataSet(unittest.TestCase):
    n = 1000
    dims = [3, 5, 10, 40]

    def test_cube_volume(self):
        for d in self.dims:
            cube = data_set.cube(self.n, d)
            assert np.all(cube <= 1.0)
            assert np.all(-1.0 <= cube)

    def test_cube_surface(self):
        for d in self.dims:
            cube = data_set.cube_surface(self.n, d)
            assert np.all(np.any((cube == 1) | (cube == -1), axis=1))

    def test_sphere_surface(self):
        for d in self.dims:
            sphere = data_set.sphere_surface(self.n, d)
            assert np.allclose(np.linalg.norm(sphere, axis=1), 1)
