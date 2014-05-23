# -*- coding: utf-8 -*-

import numpy as np


def _find_alphas(points):
    n_dimensions = len(points[0])
    n_points = len(points)  # ≙ n
    n_equations = n_dimensions + 1

    equations = np.ones((n_equations, n_points))

    # equations = | 1       ...     1   |
    #             | p[1,1]  ...  p[n,1] |
    #             | .               .   |
    #             | p[1,d]  ...  p[n,d] |
    # (d+1) x n - Matrix
    # where n = n_points and d = n_dimensions

    for dimension in range(n_dimensions):
        for i in range(n_points):
            equations[dimension + 1, i] = points[i][dimension]

    # E * a = 0
    U, s, V = np.linalg.svd(equations)

    # I don't know how exactly this works.
    # My source is http://campar.in.tum.de/twiki/pub/Chair/
    #     TeachingWs05ComputerVision/3DCV_svd_000.pdf
    # E ≙ equations, a ≙ alphas
    # || E * a || = ||U * s * V.T * a|| =   // U is an unitary matrix
    #               ||s * V.T * a|| =
    #
    alphas = V.T[:, -1]
    return alphas


def radon_point(points):
    """
    Find the `radon point <http://en.wikipedia.org/wiki/Radon%27s_theorem>`.
    points : (n, d)-array_like
        where n is the number of points and d the dimension of the points
    Return the radon point as a ndarray.
    """
    _points = np.array(points)
    n = len(_points)
    d = len(_points[0])
    assert n >= d + 2

    alphas = _find_alphas(_points)

    greater_idx = alphas >= 0
    greater_sum = np.sum(alphas[greater_idx])
    alphas_g = np.asmatrix(alphas[greater_idx]).T
    greater_points = np.asmatrix(_points[greater_idx]).T
    return np.asarray(greater_points * alphas_g / greater_sum)
