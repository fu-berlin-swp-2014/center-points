# -*- coding: utf-8 -*-

import numpy as np

from .interfaces import CenterpointAlgo


class IteratedTverberg(CenterpointAlgo):

    def centerpoint(self, points):
        pass


def _prune(alphas, hull):
    # Remove all coefficients that are already (close to) zero.
    idx_nonzero = ~ np.isclose(alphas, np.zeros_like(alphas)) # alphas != 0
    #print(idx_nonzero, alphas, hull)
    alphas = alphas[idx_nonzero]
    hull = hull[idx_nonzero]

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
    lindep = _hull[1:] - _hull[1]

    # Solve β * lindep = 0
    _, _, V = np.linalg.svd(lindep.T)
    _betas = V.T[:, -1]

    # Calculate β_1 in a way to assure Sum β_i = 0
    beta1 = np.negative(np.sum(_betas))
    betas = np.hstack((beta1, _betas))

    # Calculate the adjusted alphas and determine the minimum.
    # Calculate the minimum fraction α / β_i for each β_i > 0
    idx_positive = betas > 0
    idx_nonzero = ~ np.isclose(betas, np.zeros_like(betas))  # betas != 0
    idx = idx_positive & idx_nonzero
    lambdas = _alphas[idx] / betas[idx]
    lambda_min_idx = np.argmin(lambdas)

    # Adjust the α's of the original point
    # Since _alphas is a view to the original data, the alphas array will be
    # be updated automatically.
    _alphas[:] = _alphas - (lambdas[lambda_min_idx] * betas)

    #print("alphas':", alphas, "\nhull:", hull, "\nbetas:", betas, "\nid:", lambda_min_idx)

    # Remove (filter) the pruned hull vector.
    idx = np.arange(n) != lambda_min_idx
    hull = hull[idx]
    alphas = alphas[idx]

    #print("pt:", alphas.dot(hull), alphas.dtype)

    return _prune(alphas, hull)


# def _convex_combination(point, hull):
#     n, d = hull.shape
#
#     a = np.vstack((hull.T, np.ones(n)))
#     b = np.hstack((point, np.ones(1)))
#     x, residues, rank, s = np.linalg.lstsq(a,b)
#
#     return x
