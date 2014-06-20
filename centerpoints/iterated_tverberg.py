# -*- coding: utf-8 -*-

import numpy as np
from numpy.math import log, ceil

from .interfaces import CenterpointAlgo
from .lib import radon_partition


class IteratedTverberg(CenterpointAlgo):

    def centerpoint(self, points):
        points = np.asrray(points)
        n, d = points.shape

        # The loop terminates when a point is in the Bucket B_z
        z = log(ceil(n / (2 * ((d + 1) ** 2))))

        # Initialize empty stacks
        B = [[] for l in range(z)]

        # Push initial points with trival proofs
        for s in points:
            p = [(1, s)]
            B[0].append((s, [p]))

        while len(B[z]) == 0:
            # Initialize proof to be an empty stack
            proof = []

            # Let l be the max such that B_l−1 has at least d + 2 points
            # ToDO: optimize
            l = find_l(B, d)

            # Pop d + 2 points q_1 , . . . , q_d+2 from B_l−1
            qpoints = pop(B[l-1], d + 2)

            # TODO: radon should return gt_idx and lw_idx
            hull, radon_pt, alphas = radon_partition(qpoints)

            for k in range(2):
                # TODO: radon should return gt_idx and lw_idx
                idx = []
                qpoints_with_proofs = qpoints[idx]

                for i in range(2 ** (l - 1)):
                    # Let S_ij be the ith part of the proof for q_j
                    # ?????

                    # TODO: Access the points[gt_idx], points[lw_idx]  which contain proofs
                    # TODO: union proofs => proofs should be sets

                    # Union of all part i of the proofs.
                    # X = [q[1][i] for q in qpoints_with_proofs]
                    # TODO: make this a union

                    # X = [ (a, s), (a, s) ...  ]
                    X = []
                    for j, q in enumerate(qpoints_with_proofs):
                        # q[1][i] = [ (a, s), (a, s) ...  ]
                        for m in q[1][i]:
                            X.append(alphas[k][j] * m[0], m[1])

                    # radonpunkt ist nun in abhängigkeit der proofs dargestellt
                    # TODO: return removed hull point indices from pruning
                    X2 = _prune2(X)
                    # X2 = [ (a, s), (a,s) ...  ]
                    proof.append(X2)

                    # TODO: add the removed hull points do B_0

            B[l].append((radon_pt, proof))




# Let l be the max such that B_l−1 has at least d + 2 points
def find_l(B, d):
    l = 0
    for i, b in B:
        if len(b) >= d + 2:
            l = i

    return l + 1


def pop(l, n):
    for i in range(n):
        yield l.pop()


def _prune2(X):
    pass


def _prune(alphas, hull):
    # Remove all coefficients that are already (close to) zero.
    idx_nonzero = ~ np.isclose(alphas, np.zeros_like(alphas))  # alphas != 0
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
