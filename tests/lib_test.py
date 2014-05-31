import unittest

import numpy as np
import numpy.testing as nptest

import centerpoints.lib as lib


class TestLibrary(unittest.TestCase):
    def setUp(self):
        # { dimension -> points }
        self.d_plus_2_points = {}
        for d in [3, 5, 10, 100]:
            # we need d+2 points, first take all bases
            bases = np.eye(d)

            self.d_plus_2_points[d] = \
                np.concatenate((bases,
                                [bases[0] + bases[1],
                                 bases[1] + bases[2]]))

    def test_find_alphas(self):
        for points in self.d_plus_2_points.values():
            alphas = lib._find_alphas(points)

            self.assertEqual(type(alphas), type(np.array([])))
            self.assertEqual(len(alphas), len(points))

            smaller_idx = alphas < 0
            greater_idx = alphas >= 0
            smaller_sum = np.sum(alphas[smaller_idx])
            greater_sum = np.sum(alphas[greater_idx])

            # make sure it is not the trivial solution
            self.assertNotAlmostEqual(smaller_sum, 0)

            self.assertAlmostEqual(greater_sum + smaller_sum, 0)

    def test_radon_point(self):
        for points in self.d_plus_2_points.values():
            alphas = lib._find_alphas(points)
            radon_tuple = lib.radon_point(points)
            self.assertEqual(type(radon_tuple), np.ndarray)

            radon = np.asmatrix(radon_tuple)
            greater_alphas = np.asmatrix(alphas[alphas >= 0])
            greater_points = np.asmatrix(points[alphas >= 0])

            nptest.assert_allclose(radon / np.sum(greater_alphas),
                                   greater_alphas * greater_points)

            smaller_alphas = np.asmatrix(alphas[alphas < 0])
            smaller_points = np.asmatrix(points[alphas < 0])

            nptest.assert_allclose(smaller_alphas * smaller_points,
                                   radon / np.sum(smaller_alphas),
                                   atol=1e-15)
