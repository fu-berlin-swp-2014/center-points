
from interfaces import CenterpointAlgo
from helpers import chunks
from lib import radon
class ClarksonAlgo(CenterpointAlgo):
    def __init__(self):
        pass

    def centerpoint(points):
        dim = len(points[0])
        L = (dim+2)^4
        current_level = random.sample(points, L)
        next_level = []
        while len(next_level) != 1:
            next_level = []
            for point_sample in chunks(current_level, dim+2):
                next_level.append(radon(point_sample))

            current_level = next_level

        return next_level[0]
