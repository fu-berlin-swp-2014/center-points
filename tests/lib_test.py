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

            greater_idx = alphas > 0
            smaller_idx = ~ greater_idx
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
            greater_idx = alphas > 0
            greater_alphas = np.asmatrix(alphas[greater_idx])
            greater_points = np.asmatrix(points[greater_idx])

            sum_greater = np.sum(greater_alphas)
            nptest.assert_allclose(radon / sum_greater, radon * sum_greater)
            nptest.assert_allclose(radon / sum_greater,
                                   greater_alphas * greater_points)

            smaller_alphas = np.asmatrix(alphas[~ greater_idx])
            smaller_points = np.asmatrix(points[~ greater_idx])

            nptest.assert_allclose(smaller_alphas * smaller_points,
                                   radon / np.sum(smaller_alphas),
                                   atol=1e-15)

    def test_solve_homogeneous(self):
        M = np.array([[1, 0, 0, 0, 2],
                      [0, 0, 3, 0, 0],
                      [0, 0, 0, 0, 0],
                      [0, 4, 0, 0, 0]])

        null = lib.solve_homogeneous(M)
        nptest.assert_allclose(np.dot(M, null), np.zeros(4), atol=1e-10)

    def test_null_space(self):
        # simple example with a one dimensional null space ()
        a = np.array([[2, 3, 5], [-4, 2, 3], [0, 0, 0]])
        null_space_a = lib.null_space(a)
        x = np.dot(a, null_space_a)
        nptest.assert_allclose(np.dot(a, (2*null_space_a)),
                               np.zeros_like(null_space_a),
                               atol=1e-10)
        nptest.assert_allclose(np.dot(a, (10*null_space_a)),
                               np.zeros_like(null_space_a),
                               atol=1e-10)

        # advanced example with a 3 dimensional null space ()
        b = np.array([[1, 1, 1, 2, 3],
                      [1, 0, 1, 2, 3],
                      [1, 0, 1, 2, 3],
                      [1, 0, 1, 2, 3],
                      [1, 0, 1, 2, 3]])

        null_space_b = lib.null_space(b)

        null_vec = 2*null_space_b[:, 0] + 4*null_space_b[:, 1]
        nptest.assert_allclose(np.dot(b, null_vec),
                               np.zeros_like(null_vec),
                               atol=1e-10)
