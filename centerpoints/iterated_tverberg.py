# -*- coding: utf-8 -*-

from itertools import compress

import numpy as np
from numpy import log, log10, ceil

from centerpoints.helpers import pop
from centerpoints.lib import solve_homogeneous, radon_partition
from centerpoints.interfaces import CenterpointAlgo


class IteratedTverberg(CenterpointAlgo):

    def centerpoint(self, points):
        points = np.asarray(points)
        n, d = points.shape

        # The loop terminates when a point is in the bucket B_z
        z = int(log10(ceil(n / (2 * ((d + 1) ** 2)))))
        # or if the paper has a typo 
        # z = int(ceil(log10(n / (2 * ((d + 1) ** 2)))))


        # Initialize empty stacks / buckets
        B = [[] for l in range(z+1)]

        # Push initial points with trivial proofs
        # Proofs consist of a factor and a hull.
        for s in points:
            # TODO (one could copy the proof to be save)
            proof = [(1, s)]
            B[0].append((s, [proof]))

        while len(B[z]) == 0:
            # Initialize proof to be an empty stack
            proof = []

            # Let l be the max such that B_l−1 has at least d + 2 points
            # ToDO: optimize?
            l = find_l(B, d)

            # Pop d + 2 points q_1 , . . . , q_d+2 from B_l−1
            # qs denotes the list of points q_1 to q_d+2
            # qss denotes the collection of proofs for each point q_i
            qs_with_proof = pop(B[l-1], d + 2)
            qs, pss = zip(*qs_with_proof)

            # TODO: the proof parts should be "ordered" according to the paper

            # Calculate the radon partition
            radon_pt, alphas, partition_masks = radon_partition(qs)

            for k in range(2):
                # qs_part denotes the list of points in this partition
                # qs_part = list(compress(qs, partition_masks[k]))

                # pss_part denotes the collection of proofs for that points
                pss_part = list(compress(pss, partition_masks[k]))

                # as_part denotes the factors of the radon point in regard to
                # the hulls consisting of the partitions
                as_part = alphas[k]

                # Form a proof of depth 2^(l+1) for the radon point
                for i in range(2 ** (l - 1)):

                    # Union the i'th part of each proof of each point
                    X_alphas = []
                    X_hulls = []
                    for j, ps in enumerate(pss_part):
                        S_ij = ps[i]

                        for ppt in S_ij:
                            # Adjust the factors of the proofs to be able to
                            # describe the radon point as a combination of it's
                            # proofs.
                            alpha = as_part[j] * ppt[0]
                            hull = ppt[1]

                            # Add them to the new proof
                            X_alphas.append(alpha)
                            X_hulls.append(hull)

                    # Reduce the hull of the radon point, that is consisting
                    # of the proof parts, to d + 1 hull points.
                    X2, non_hull = _prune_zipped(X_alphas, X_hulls)

                    proof.append(X2)
                    B[0].extend(non_hull)

            B[l].append((radon_pt, proof))

        return B[z][0][0]


# Let l be the max such that B_l−1 has at least d + 2 points
def find_l(B, d):
    l = None
    for i, b in enumerate(B):
        if len(b) >= d + 2:
            l = i

    assert (l != None), "No bucket with d+2 points found"

    return l + 1


def _prune_zipped(alphas, hull):
    _alphas = np.asarray(alphas)
    _hull = np.asarray(hull)
    alphas, hull, non_hull = _prune_recursive(_alphas, _hull, [])

    assert (alphas.shape[0] == hull.shape[0]), "Broken hull"

    non_hull = [(p, [[(1, p)]]) for p in non_hull]

    return zip(alphas, hull), non_hull


def _prune_recursive(alphas, hull, non_hull):
    # Remove all coefficients that are already (close to) zero.
    idx_nonzero = ~ np.isclose(alphas, np.zeros_like(alphas))  # alphas != 0
    alphas = alphas[idx_nonzero]

    # Add pruned points to the non hull (and thus back to bucket B_0)
    non_hull = non_hull + hull[~idx_nonzero].tolist()

    hull = hull[idx_nonzero]

    # @see http://www.math.cornell.edu/~eranevo/homepage/ConvNote.pdf
    # http://en.wikipedia.org/wiki/Carath%C3%A9odory's_theorem_(convex_hull)
    n, d = hull.shape

    # Anchor: d + 1 hull points can't be reduced any further
    if n <= d + 1:
        return alphas, hull, non_hull

    # Choose d + 2 hull points
    _hull = hull[:d + 2]
    _alphas = alphas[:d + 2]

    # Create linearly dependent vectors
    lindep = _hull[1:] - _hull[1]

    # Solve β * lindep = 0
    _betas = solve_homogeneous(lindep.T)

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

    # Remove (filter) the pruned hull vector.
    idx = np.arange(n) != lambda_min_idx
    hull = hull[idx]
    non_hull.append(hull[lambda_min_idx])
    alphas = alphas[idx]

    return _prune_recursive(alphas, hull, non_hull)
