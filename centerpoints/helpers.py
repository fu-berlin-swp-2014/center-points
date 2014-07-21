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


def random_sphere_points(n_points, dim, r=1):
    assert dim == 3

    # @see http://en.wikipedia.org/wiki/Spherical_coordinate_system
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

    # Build the cartesian product to generate n_total points (combinations).
    # There are no two points with the same angles.
    # TODO: Problem in regard to f.ex.h sin 0 =~= pi
    ang = cartesian(angspace).T

    # Create an array of n - 1 angles for each point.
    # ang = np.zeros((dim - 1, n_total), dtype=np.float64)
    # for i in range(n_total):
    #     for j in range(dim - 1):
    #         k = (i // (n_dim ** j)) % n_dim
    #         ang[j][i] = angspace[j][k]

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


def cartesian(arrays, out=None):
    """
    Generate a cartesian product of input arrays.

    Parameters
    ----------
    arrays : list of array-like
        1-D arrays to form the cartesian product of.
    out : ndarray
        Array to place the cartesian product in.

    Returns
    -------
    out : ndarray
        2-D array of shape (M, len(arrays)) containing cartesian products
        formed of input arrays.

    Examples
    --------
    >>> cartesian(([1, 2, 3], [4, 5], [6, 7]))
    array([[1, 4, 6],
           [1, 4, 7],
           [1, 5, 6],
           [1, 5, 7],
           [2, 4, 6],
           [2, 4, 7],
           [2, 5, 6],
           [2, 5, 7],
           [3, 4, 6],
           [3, 4, 7],
           [3, 5, 6],
           [3, 5, 7]])


    (c) http://stackoverflow.com/a/1235363
    """

    arrays = [np.asarray(x) for x in arrays]
    dtype = arrays[0].dtype

    n = np.prod([x.size for x in arrays])
    if out is None:
        out = np.zeros([n, len(arrays)], dtype=dtype)

    m = n / arrays[0].size
    out[:, 0] = np.repeat(arrays[0], m)
    if arrays[1:]:
        cartesian(arrays[1:], out=out[0:m, 1:])
        for j in range(1, arrays[0].size):
            out[j*m:(j+1)*m, 1:] = out[0:m, 1:]
    return out
