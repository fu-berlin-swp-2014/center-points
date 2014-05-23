from math import log, ceil

import numpy as np

from .interfaces import CenterpointAlgo
from .helpers import chunks
from .lib import radon_point


class ClarksonAlgo(CenterpointAlgo):
    def __init__(self):
        pass

    # algo1
    def centerpoint(self, points):
        dim = len(points[0])
        # TODO: check L size and required number of points.
        L = (dim + 2) ** 4

        nodes = _sample(points, L)
        while len(nodes) != 1:
            nodes = [radon_point(chunk) for chunk in chunks(nodes, dim + 2)]

        return nodes[0]

    def algo4(self, points):
        dim = len(points[0])
        n = len(points)

        assert (n >= dim ** 4 + log(log(n)))

        z = ceil(dim + log(log(n)))

        T = points
        for i in range(z):
            T = [radon_point(sample) for sample in _sample(T, dim + 2, n)]

        return T[0]


# TODO: Document and move to lib/helpers
def _sample(population, trials, count=None):
    size = trials if count is None else (count, trials)
    ids = np.random.randint(len(population), size=size)
    return np.asarray(population)[ids]