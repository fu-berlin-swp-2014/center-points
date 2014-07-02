from math import log, ceil

from .interfaces import CenterpointAlgo
from .helpers import chunks
from .lib import radon_point, sample_with_replacement


class ClarksonAlgo(CenterpointAlgo):
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
