# -*- coding: utf-8 -*-

import numpy as np


def _find_alphas(points):
    _points = np.asarray(points)

    n_points, n_dimensions = _points.shape
    n_equations = n_dimensions + 1

    # equations = | 1       ...     1   |
    #             | p[1,1]  ...  p[n,1] |
    #             | .               .   |
    #             | p[1,d]  ...  p[n,d] |
    # (d+1) x n - Matrix
    # where n = n_points and d = n_dimensions

    equations = _points.T
    ones = np.ones(n_points)
    equations = np.vstack((np.ones(n_points), equations))

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
    _points = np.asarray(points)
    n, d = _points.shape
    assert n >= d + 2

    alphas = _find_alphas(_points)

    greater_idx = alphas >= 0
    greater_alphas = np.asmatrix(alphas[greater_idx])
    greater_sum = np.sum(greater_alphas)
    greater_points = np.asmatrix(_points[greater_idx])

    radon_pt = (greater_alphas / greater_sum) * greater_points

    # Return the radon point as a ndarray and the correct dimension.
    assert radon_pt.shape == (1, d)
    radon_pt = np.asarray(radon_pt)
    radon_pt.shape = d

    return radon_pt


def sample_with_replacement(population, k, n=None):
    """
    Return a sample of size k with replacements chosen from the population.
    If n is set, an array of size n containing samples of size k is returned.

    :param population:
    :param k: size of the sample
    :param n: number of samples
    :return: n (or 1) samples of size k
    """
    size = k if n is None else (n, k)
    ids = np.random.randint(len(population), size=size)
    return np.asarray(population)[ids]
