import math
import numpy as np

from math import pi, cos, sin


def random_sphere_points(n_points, dim):
    assert dim == 3

    # @see http://en.wikipedia.org/wiki/Spherical_coordinate_system
    r = 1
    theta = np.random.rand(n_points) * 2 * math.pi
    phi = np.random.rand(n_points) * 2 * math.pi

    x = r * np.sin(theta) * np.cos(phi)
    y = r * np.sin(theta) * np.sin(phi)
    z = r * np.cos(theta)

    return np.column_stack((x, y, z))


def sphere_points(n, r=1):
    #  assert (n % 2 == 0)

    nn = math.log2(n)

    pi2_steps = np.arange(0, 2*pi, step=(2*pi / nn))
    pi_steps = np.arange(0, pi, step=(pi / nn))

    points = []
    for i in pi2_steps:
        for j in pi_steps:
            x = r * cos(i) * sin(j)
            y = r * sin(i) * sin(j)
            z = r * cos(j)
            points.append((x, y, z))

    np_points = np.asarray(points)
    return np_points
