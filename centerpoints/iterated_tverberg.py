# -*- coding: utf-8 -*-

import numpy as np

from .interfaces import CenterpointAlgo


class IteratedTverberg(CenterpointAlgo):

    def centerpoint(self, points):
        pass


def _prune(alphas, hull):
    # @see http://www.math.cornell.edu/~eranevo/homepage/ConvNote.pdf
    # http://en.wikipedia.org/wiki/Carath%C3%A9odory's_theorem_(convex_hull)
    n, d = hull.shape

    # Anchor: d + 1 hull points can't be reduced any further
    if n <= d + 1:
        return alphas, hull

    # Choose d + 2 hull points
    _hull = hull[:d + 2]
    _alphas = alphas[:d + 2]

    # Create linearly dependent vectors
    ld = _hull[1:] - _hull[1]

    # Solve β * ld = 0
    _, _, V = np.linalg.svd(ld.T)
    _betas = V.T[:, -1]

    # Calculate β_1 in a way to assure Sum β_i = 0
    _beta1 = - np.sum(_betas)
    betas = np.hstack((_beta1, _betas))

    # Calculate the adjusted alphas and determine the minimum.
    lambdas = _alphas / betas
    lambda_min_idx = np.argmin(lambdas)

    # Adjust the α's of the original point
    alphas = alphas[:]
    alphas[:d + 2] = _alphas - (lambdas[lambda_min_idx] * betas)

    idx = np.arange(n) != lambda_min_idx
    hull = hull[idx]
    alphas = alphas[idx]

    return _prune(alphas, hull)


# def _convex_combination(point, hull):
#     n, d = hull.shape
#
#     a = np.vstack((hull.T, np.ones(n)))
#     b = np.hstack((point, np.ones(1)))
#     x, residues, rank, s = np.linalg.lstsq(a,b)
#
#     return x

