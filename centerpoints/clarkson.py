from math import log, ceil

from .interfaces import CenterpointAlgo
from .helpers import chunks
from .lib import radon_point, sample_with_replacement, radon_partition
import centerpoints.visualise.visualise as vis


class ClarksonAlgo(CenterpointAlgo):
    def __init__(self):
        pass

    # algo1
    def centerpoint(self, points):
        dim = len(points[0])
        # TODO: check L size and required number of points.
        L = (dim + 2) ** 4

        nodes = sample_with_replacement(points, L)
        while len(nodes) != 1:
            nodes = [radon_point(chunk) for chunk in chunks(nodes, dim + 2)]

        return nodes[0]

    def visualisation(self, points, v):
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

                (smaller, bigger), radon_pt, _ = radon_partition(chunk)
                v.add(vis.RadonPartition(smaller, bigger, radon_pt, color))
                new_nodes.append(radon_pt)
            i += 1
            nodes = new_nodes

        v.next("Approximated Centerpoint")
        v.point(nodes[0], (1, 1, 1, 1), 5)
        return nodes[0]

    def algo4(self, points):
        dim = len(points[0])
        n = len(points)

        assert (n >= dim ** 4 + log(log(n)))

        z = ceil(dim + log(log(n)))

        T = points
        for i in range(z):
            T = [radon_point(sample)
                 for sample in sample_with_replacement(T, dim + 2, n)]

        return T[0]
