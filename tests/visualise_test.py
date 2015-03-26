import math
import unittest

import numpy as np
from centerpoints.visualise \
    import Visualisation, Polygons, Points, PointGroups, Gui


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


class TestVisualisation(unittest.TestCase):

    def test_points(self):
        vis = Visualisation()

        n_points = 10000
        points = random_sphere_points(n_points, 3) * 300

        colors = np.random.rand(n_points, 4)
        colors[:, 3] = np.ones((n_points, ))
        colors.astype(np.float32)
        vis.add(Points(points, colors))
        # uncomment to show the visualisation
        # vis.show()

    def test_polygons(self):
        vis = Visualisation()

        polygons = Polygons(np.array([[
            [1, 0, 0],
            [1, 1, 0],
            [0, 1, 0],
            [0, 0, 0],
            [1, 0, 0],
        ]]) * 100 + 100, (1, 0, 0, 1))
        vis.add(polygons)
        vis.draw_axes = True
        # uncomment to show the visualisation
        # vis.show()

    def test_pointgroups(self):
        group = PointGroups()
        group.new_group(np.random.rand(1000, 3) * 100 + 100)
        group.new_group(np.random.rand(1000, 3) * 100 - 100)
        group.new_group(np.random.rand(1000, 3) * 100)

        assert group.color(0) == (1, 0, 0, 1)
        assert group.color(1) == (0, 1, 0, 1)
        assert group.color(2) == (0, 0, 1, 1)

        vis = Visualisation()
        vis.add(group)
        # uncomment to show the visualisation
        # vis.show()

    def test_visualisation_gui(self):
        gui = Gui()
        # uncomment to show the window
        # gui.app.exec_()
