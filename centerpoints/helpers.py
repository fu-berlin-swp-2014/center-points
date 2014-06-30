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


class NumpyAwareJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray) and obj.ndim == 1:
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


def random_sphere_points(n_points, dim):
    assert dim == 3

    # @see http://en.wikipedia.org/wiki/Spherical_coordinate_system
    r = 1
    theta = np.random.rand(n_points) * pi
    phi = np.random.rand(n_points) * 2 * pi

    x = r * np.sin(theta) * np.cos(phi)
    y = r * np.sin(theta) * np.sin(phi)
    z = r * np.cos(theta)

    return np.column_stack((x, y, z))


def sphere_points(n, dim, r=1):
    """

    :param n: At least n points will be generated.
    :param dim:
    """

    # Calculate the (dim-1)'th root of n, which is the number of iterations per
    # dimension.
    n_dim = ceil(n ** (1. / (dim - 1)))
    n_total = n_dim ** (dim - 1)

    # The first dim -1 angles range from [0, pi] and the last from [0, 2pi[.
    # @see http://en.wikipedia.org/wiki/N-sphere
    angspace = np.zeros((dim - 1, n_dim), dtype=np.float64)
    angspace[:-1] = np.linspace(0, pi, n_dim)
    angspace[-1] = np.linspace(0, 2 * pi, n_dim + 1)[:-1]

    # Create an array of n - 1 angles for each point.
    # There are no two points with the same angles.
    # TODO: Problem in regard to f.ex.h sin 0 =~= pi
    ang = np.zeros((dim - 1, n_total), dtype=np.float64)
    for i in range(n_total):
        for j in range(dim - 1):
            k = (i // (n_dim ** j)) % n_dim
            ang[j][i] = angspace[j][k]

    # The spherical coordinates will be calculated as shown in
    # @see http://en.wikipedia.org/wiki/N-sphere#Spherical_coordinates
    points = np.zeros((n_total, dim))
    _points = points.T

    _points[0] = r * np.cos(ang[0])
    sin_cum = r
    for i in range(1, dim - 1):
        sin_cum *= np.sin(ang[i-1])
        _points[i] = sin_cum * np.cos(ang[i])

    _points[-1] = sin_cum * np.sin(ang[-1])

    np.random.shuffle(points)

    return points
