# -*- coding: utf-8 -*-
import numpy as np


def _find_alphas(points):
    _points = np.asarray(points)

    n_points, n_dimensions = _points.shape

    # equations = | 1       ...     1   |
    #             | p[1,1]  ...  p[n,1] |
    #             | .               .   |
    #             | p[1,d]  ...  p[n,d] |
    # (d+1) x n - Matrix
    # where n = n_points and d = n_dimensions

    equations = np.vstack((np.ones(n_points), _points.T))

    return solve_homogeneous2(equations)


# I don't know how exactly this works.
# My source is http://campar.in.tum.de/twiki/pub/Chair/
# TeachingWs05ComputerVision/3DCV_svd_000.pdf
# E ≙ equations, a ≙ alphas
# || E * a || = ||U * s * V.T * a|| =   // U is an unitary matrix
#               ||s * V.T * a|| =
#
# Implemenation see also:
# http://stackoverflow.com/questions/1835246
# /how-to-solve-homogeneous-linear-equations-with-numpy
def solve_homogeneous(A, eps=1e-15):
    assert(isinstance(A, np.ndarray))

    n, d = A.shape

    U, s, V = np.linalg.svd(A, full_matrices=False)
    nullspace = np.compress(s < eps, V, axis=0)

    return nullspace


def solve_homogeneous2(A):
    assert(isinstance(A, np.ndarray))

    n, d = A.shape

    U, s, V = np.linalg.svd(A, full_matrices=True)
    nullspace = V[-1]

    return nullspace


def radon_partition(points):
    """
    Find a radon partition <http://en.wikipedia.org/wiki/Radon%27s_theorem>.

    points : (n, d)-array_like
        where n is the number of points and d the dimension of the points

    Return the radon partitions I and J, the radon point and its alphas.
        (I, J),
        (radon point),
        (alphas_I, alphas_J)
    """
    _points = np.asarray(points)
    n, d = _points.shape
    assert n >= d + 2

    alphas = _find_alphas(_points)

    greater_idx = alphas > 0
    greater_alphas = alphas[greater_idx]
    greater_points = _points[greater_idx]

    lower_idx = ~ greater_idx
    lower_alphas = alphas[lower_idx]
    lower_points = _points[lower_idx]

    sum_alphas = np.sum(greater_alphas)
    radon_pt_greater_alphas = greater_alphas / sum_alphas
    radon_pt_lower_alphas = lower_alphas / (- sum_alphas)

    radon_pt = np.dot(radon_pt_greater_alphas, greater_points)

    return (radon_pt,
            (radon_pt_greater_alphas, radon_pt_lower_alphas),
            (greater_idx, lower_idx))


def radon_point(points):
    """
    Find the `radon point <http://en.wikipedia.org/wiki/Radon%27s_theorem>`.
    points : (n, d)-array_like
        where n is the number of points and d the dimension of the points
    Return the radon point as a ndarray.
    """
    radon_pt, _, _ = radon_partition(points)
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
