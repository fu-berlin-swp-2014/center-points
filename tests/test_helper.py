import math
import numpy as np


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
