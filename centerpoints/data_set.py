import numpy as np


def _normalize(x):
    _, dim = x.shape
    norm = np.linalg.norm(x, axis=1).repeat(dim)
    return x / norm.reshape(x.shape)


def _in_sphere(points, radius=1):
    return points[(points**2).sum(axis=1) <= radius]


def sphere_surface(n=1000, d=3):
    """
    Generates `n` random points on the surface of a `d`-dimensional unit
    sphere.
    """
    unit_cube = cube(3*n, d)
    sphere_points = _in_sphere(unit_cube)[0:n]
    return _normalize(sphere_points)


def sphere_volume(n=1000, d=3):
    """
    Generates `n` random points in a `d`-dimensional unit sphere.
    """
    rand_points = cube(3*n, d)
    sphere_points = _in_sphere(rand_points)
    return sphere_points[0:n]


def cube(n=1000, d=3):
    """
    Generates `n` random points in a `d`-dimensional unit cube.
    """
    return 2*np.random.rand(n, d)-1


def cube_surface(n=1000, d=3):
    """
    Generates `n` random points on the surface of a `d`-dimensional unit
    cube.
    """
    c = cube(n, d)

    which_zeros = d * np.random.rand(n, 1)
    for i in range(d):
        idx = np.zeros(c.shape, dtype=bool)
        idx[:, i] = ((i <= which_zeros) & (which_zeros < i+1)).reshape(1000)

        # decide if the point is projected on the top or the bottom plane
        one_or_two = np.ceil(2*np.random.rand(np.count_nonzero(idx)))
        minus_or_plus_one = 2*(one_or_two - 1.5)
        c[idx] = minus_or_plus_one

    return c


def normal_distribution(n=1000, d=3):
    """
    Generates `n` random points of a `d`-dimensional multivariante normal
    distribution.
    """
    return np.random.normal(size=(n, d))
