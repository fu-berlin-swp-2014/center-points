from math import log, ceil

import numpy as np

from .interfaces import CenterpointAlgo
from .helpers import chunks
from .lib import radon_point, sample_with_replacement, radon_partition


class IteratedRadon(CenterpointAlgo):
    def __init__(self, use_tree=False):
        self._use_tree = use_tree

    def centerpoint(self, points):
        if self._use_tree:
            return self._algo1(points)
        else:
            return self._algo4(points)

    def _algo1(self, points):
        dim = len(points[0])
        # TODO: check L size and required number of points.
        L = (dim + 2) ** 4

        nodes = sample_with_replacement(points, L)
        while len(nodes) != 1:
            nodes = [radon_point(chunk) for chunk in chunks(nodes, dim + 2)]

        return nodes[0]

    def visualisation(self, points, v):
        import centerpoints.visualise as vis
        dim = len(points[0])
        # TODO: check L size and required number of points.
        L = (dim + 2) ** 4
        nodes = sample_with_replacement(points, L)
        v.points(nodes, (1, 0.5, 0, 1))
        colorgroup = vis.ColorGroup()

        i = 0
        while len(nodes) != 1:
            v.next("Iteration #" + str(i))
            new_nodes = []
            color = colorgroup.next_member()
            for chunk in chunks(nodes, dim + 2):
                print(type(chunk))
                radon_pt, _, (mask_I, mask_J) = radon_partition(chunk)
                v.add(vis.RadonPartition(chunk[mask_I, :], chunk[mask_J, :],
                                         radon_pt, color))
                new_nodes.append(radon_pt)
            i += 1
            nodes = np.asarray(new_nodes)

        v.next("Approximated Centerpoint")
        v.point(nodes[0], (1, 1, 1, 1), 5)
        return nodes[0]

    def _algo4(self, points):
        dim = len(points[0])
        n = len(points)

        assert (n >= dim ** 4 + log(log(n)))

        z = ceil(dim + log(log(n)))

        T = points
        for i in range(z):
            T = [radon_point(sample)
                 for sample in sample_with_replacement(T, dim + 2, n)]

        return T[0]
