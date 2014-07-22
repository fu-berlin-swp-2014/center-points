import json
from math import ceil, pi
import numpy as np


def has_valid_dimension(l, d=None):
    """Check congruent dimensions in a two-dimensional list."""
    if not l:
        return False

    if d is None:
        d = len(l[0])

    for sub in l:
        if len(sub) != d:
            return False

    return True


def has_valid_type(l, t):
    """ Check if every element in a two-dimensional list has the same type."""
    for sub in l:
        for e in sub:
            if type(e) != t:
                return False

    return True


def chunks(l, n):
    """ Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def pop(l, n):
    """
        Yield n elements from the list l.
        Throws IndexError if len(l) < n.
    """
    for i in range(n):
        yield l.pop()


class NumpyAwareJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray) and obj.ndim == 1:
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


def uniform_sphere_points(n, dim, r=1):
    """
    George Marsaglia: Choosing a Point from the Surface of a Sphere
    @see http://projecteuclid.org/euclid.aoms/1177692644
    """
    normal_deviates = np.random.normal(size=(dim, n))

    radius = np.sqrt((normal_deviates ** 2).sum(axis=0))
    points = normal_deviates / radius

    points = r * points

    return points.T


def uniform_sphere_points_volume(n, dim, r=1):
    """
    @see http://math.stackexchange.com/a/87238
    """
    points = uniform_sphere_points(n, dim, 1)
    uniform_deviates = np.random.uniform(size=n)

    _points = r * (uniform_deviates ** (1 / dim)) * points.T

    return _points.T


def normal_distributed_points(n, dim):
    _points = np.random.normal(size=(dim,n))
    return _points.T
