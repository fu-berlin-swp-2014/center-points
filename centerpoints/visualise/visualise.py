import time
import colorsys
import sys

from PySide import QtGui, QtOpenGL, QtCore
from PySide.QtCore import QTimer, SIGNAL
from PySide.QtGui import QLabel
import copy
import numpy as np

from OpenGL.GL import *
from OpenGL.GLU import *

import centerpoints.data_set


class Color:
    def __init__(self, color=None):
        if type(color) is np.ndarray:
            self._color = color

        elif color is None:
            self._color = (1, 1, 1, 1)

        elif type(color) is int:
            self._color = (color & 0x00FF0000 >> 16,
                           color & 0x0000FF00 >> 8,
                           color & 0x000000FF,
                           color & 0xFF000000 >> 24)
        elif type(color) == tuple:
            self._color = color
        else:
            raise ValueError(str(type(color)) + " is not supported")

        if type(self._color) is tuple:
            if max(self._color) > 1:
                self._color = (c / 255 for c in self._color)

    def check_size(self, size):
        if self._color == np.ndarray:
            assert size == len(gl_array(self._color.flatten().tolist()))

    def gl_array(self, n_points):
        if type(self._color) is np.ndarray:
            arr = self._color
        else:
            arr = np.zeros((n_points + 2, 4))
            for i, c in enumerate(self._color):
                arr[:, i].fill(c)
        return gl_array(arr.flatten().tolist())


class Camera(object):
    ISOMETRIC = 0
    PROJECTIVE = 1

    MODES = [ISOMETRIC, PROJECTIVE]

    mode = PROJECTIVE
    x, y, z = 0, 0, 512
    rotx, roty, rotz = 30, -45, 0
    w, h = 640, 480
    far = 2048
    fov = 60

    def set_size(self, width, height):
        """ Adjust window size.
        """
        self.w, self.h = width, height
        glViewport(0, 0, width, height)
        print(("Viewport " + str(width) + "x" + str(height)))
        self.update_projection()

    def update_projection(self):
        if self.mode == self.ISOMETRIC:
            self.isometric()
        elif self.mode == self.PROJECTIVE:
            self.perspective()

    def isometric(self):
        self.mode = self.ISOMETRIC
        """ Isometric projection.
        """
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(-self.w/2., self.w/2., -self.h/2., self.h/2., 0, self.far)
        glMatrixMode(GL_MODELVIEW)

    def perspective(self):
        """ Perspective projection.
        """
        self.mode = self.PROJECTIVE
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.fov, float(self.w)/self.h, 0.1, self.far)
        glMatrixMode(GL_MODELVIEW)

    def drag(self, x, y, dx, dy, button, modifiers):
        """ Mouse drag event handler. """
        if button == 1:
            self.x -= dx*2
            self.y -= dy*2
        elif button == 2:
            self.x -= dx*2
            self.z -= dy*2
        elif button == 4:
            self.roty += dx/4.
            self.rotx -= dy/4.

    def apply(self):
        """ Apply camera transformation. """
        glLoadIdentity()
        glTranslatef(-self.x, -self.y, -self.z)
        glRotatef(self.rotx, 1, 0, 0)
        glRotatef(self.roty, 0, 1, 0)
        glRotatef(self.rotz, 0, 0, 1)


def gl_array(list):
    """ Converts a list to GLFloat list.
    """
    return (GLdouble * len(list))(*list)


def draw_vertex_array(vertices, colors=None, mode=GL_LINES):
    """ Draw a vertex array.
    """
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_COLOR_ARRAY)

    if colors is None:
        colors = Color()

    gl_colors = colors.gl_array(len(vertices) / 3)
    glVertexPointer(3, GL_DOUBLE, 0, vertices)
    glColorPointer(4, GL_DOUBLE, 0, gl_colors)
    glDrawArrays(mode, 0, int(len(vertices) / 3))

    glDisableClientState(GL_VERTEX_ARRAY)
    glDisableClientState(GL_COLOR_ARRAY)


# TODO:
def draw_point(point, color, size=1):
    glPointSize(size)
    glBegin(GL_POINTS)
    glColor4f(*color)
    glVertex3f(*point)
    glEnd()
    glPointSize(1)


def numpy2polygon(points):
   # if (points[0] != points[-1]).any():
    #    points = np.vstack((points, points[0, :]))
    return points


def numpy2polygons(polygons):
    return np.array([numpy2polygon(p) for p in polygons], dtype=np.float32)


class VisualisationController(QtGui.QMainWindow):
    def __init__(self, data=None, data_name="Data Points", n_data=1000,
                 dim_data=3, data_func=None, algorithm=None, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        import centerpoints.iterated_radon

        # _visualisation and _central_widget will be set in
        # update_visualisation()
        self._visualisation = None
        self._central_widget = None
        self.n_data = n_data
        self.dim_data = dim_data
        self._data_name = "Data Points"
        self._scale_factor = 100
        if data is not None:
            self._data = data
        else:
            if data_func is None:
                data_func = centerpoints.data_set.sphere_volume
                self._data_name = "Sphere Volume"
            self._data_func = data_func

            self._data = self._data_func(self.n_data, self.dim_data)

        if algorithm is None:
            algorithm = centerpoints.iterated_radon.IteratedRadon()
        self._algorithm = algorithm

        # Setup Gui
        self._algo_menu = QtGui.QMenu("Algorithms", self)
        algorithms = {
            # Add new algorithms here
            "Iterated Radon": centerpoints.iterated_radon.IteratedRadon()
        }
        for name, cls in algorithms.items():
            action = self._algo_menu.addAction(name)
            action.triggered.connect(
                lambda c=cls: self.set_algorithm(c)
            )

        self.menuBar().addMenu(self._algo_menu)

        self._data_menu = QtGui.QMenu("Data Sets", self)
        data_sets = {
            "Cube Volume": centerpoints.data_set.cube,
            "Cube Surface": centerpoints.data_set.cube_surface,
            "Normal Distribution": centerpoints.data_set.normal_distribution,
            "Sphere Surface": centerpoints.data_set.sphere_surface,
            "Sphere Volume": centerpoints.data_set.sphere_volume,
        }
        for name, func in sorted(data_sets.items()):
            self._data_menu.addAction(name).triggered.connect(
                lambda n=name, f=func: self.set_data_func(n, f)
            )

        self.menuBar().addMenu(self._data_menu)
        self.update_visualisation()
        self.setWindowTitle(self.tr("Centerpoints"))

    def set_data(self, name, data):
        self._data_name = name
        self._data = data
        self.update_visualisation()

    def set_algorithm(self, algo_class):
        self._algorithm = algo_class
        self.update_visualisation()

    def set_data_func(self, name, data_func):
        print(name)
        self._data_name = name
        self._data_func = data_func
        self.update_visualisation()

    def update_visualisation(self):
        if self._data_func is not None:
            self._data = \
                self._scale_factor * self._data_func(self.n_data, self.dim_data)

        self._visualisation = Visualisation(
            start_step=Step(description=self._data_name))
        self._visualisation.points(self._data, (0.5, 0.5, 0.5, 0.5))
        self._algorithm.visualisation(self._data,
                                      self._visualisation)

        if self._central_widget is not None:
            self._central_widget.deleteLater()
        self._central_widget = VisualisationWidget(
            self._visualisation, parent=self)

        self.setCentralWidget(self._central_widget)


class VisualisationWidget(QtGui.QWidget):
    def __init__(self, visualisation, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self._visualisation = visualisation
        self._glWidget = GLWidget(visualisation)
        self._stepsList = QtGui.QListWidget()
        self._stepsList.setMaximumWidth(200)
        self._stepsList.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)

        for i, s in enumerate(self._visualisation._steps):
            self._stepsList.addItem(s.description)

        self._mainLayout = QtGui.QHBoxLayout()
        self._mainLayout.addWidget(self._stepsList)
        self._glOptionLayout = QtGui.QVBoxLayout()
        self._glOptionLayout.addWidget(self._glWidget)

        self._optionLayout = QtGui.QHBoxLayout()
        self._animate_btn = QtGui.QPushButton("Animate")
        self._animate_btn.setCheckable(True)
        self._animate_btn.clicked.connect(
            lambda: self._glWidget.toggle_animation())

        self._optionLayout.addWidget(self._animate_btn)

        self._animate_slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self._animate_slider.valueChanged.connect(
            lambda s: self._glWidget.set_animation_speed((100 - s) / 10))

        self._optionLayout.addWidget(QLabel("Animation Speed:"))
        self._optionLayout.addWidget(self._animate_slider)

        self._show_axis_btn = QtGui.QPushButton("Show Coordinate System")
        self._show_axis_btn.setCheckable(True)
        self._show_axis_btn.clicked.connect(
            self._glWidget.toggle_axis)
        self._optionLayout.addWidget(self._show_axis_btn)

        self._glOptionLayout.addLayout(self._optionLayout)

        self._mainLayout.addLayout(self._glOptionLayout)

        self._stepsList.selectAll()

        self._stepsList.connect(SIGNAL("itemSelectionChanged()"),
                                self.changedSelection)

        self.setLayout(self._mainLayout)


    def changedSelection(self):
        indexes = [i.row() for i in self._stepsList.selectedIndexes()]
        steps = self._visualisation._steps
        for i in range(len(steps)):
            steps[i].selected = i in indexes


class GLWidget(QtOpenGL.QGLWidget):
    KEY_DOWN_ROTATE = [QtCore.Qt.Key_Down]
    KEY_TOP_ROTATE = [QtCore.Qt.Key_Up]
    KEY_LEFT_ROTATE = [QtCore.Qt.Key_Left]
    KEY_RIGHT_ROTATE = [QtCore.Qt.Key_Right]
    KEY_FARER = [QtCore.Qt.Key_W, QtCore.Qt.Key_Plus]
    KEY_NEARER = [QtCore.Qt.Key_S, QtCore.Qt.Key_Minus]

    def __init__(self, visualisation, parent=None, cam=None, fps=30):
        QtOpenGL.QGLWidget.__init__(self, parent)
        if cam is None:
            cam = Camera()

        self._visualisation = visualisation

        self.steps_delay = 1
        self.axis_factor = 50
        self._start_time = time.time()
        self.animation_speed = 1
        self.animation = False
        self.show_axis = True

        self.cam = cam
        self.initOpenGL()
        self.last_mouse_pos = QtCore.QPoint()
        self.timer = QTimer()
        self.connect(self.timer, SIGNAL("timeout()"), self.updateGL)
        self.timer.start()
        self.timer.setInterval(1000 / fps)
        self.setFocusPolicy(QtCore.Qt.ClickFocus)

    def initOpenGL(self):
        """ Initial OpenGL configuration. """
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDepthFunc(GL_LEQUAL)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.cam.apply()
        self._draw_visualisation()

    def repaint(self, *args, **kwargs):
        self.paintGL()

    def resizeGL(self, width, height):
        self.cam.set_size(width, height)

    def mousePressEvent(self, event):
        self.last_mouse_pos = QtCore.QPoint(event.pos())

    def mouseMoveEvent(self, event):
        dx = event.x() - self.last_mouse_pos.x()
        dy = event.y() - self.last_mouse_pos.y()
        if event.buttons() & QtCore.Qt.LeftButton:
            self.cam.rotx += dy
            self.cam.roty += dx
        elif event.buttons() & QtCore.Qt.RightButton:
            self.cam.rotx += 8 * dy
            self.cam.roty += 8 * dx

        self.last_mouse_pos = QtCore.QPoint(event.pos())

    def keyPressEvent(self, event):
        # TODO: refactor
        key = event.key()
        print(key)
        print()
        delta = 10
        if key == QtCore.Qt.Key_P:
            self.cam.perspective()
        elif key == QtCore.Qt.Key_I:
            self.cam.isometric()
        elif key == QtCore.Qt.Key_W:
            self.cam.z -= delta
        elif key == QtCore.Qt.Key_S:
            self.cam.z += delta
        elif key == QtCore.Qt.Key_A:
            self.cam.x -= delta
        elif key == QtCore.Qt.Key_D:
            self.cam.x += delta
        elif self._is_in(key, self.KEY_LEFT_ROTATE):
            self.cam.roty -= 4.
        elif self._is_in(key, self.KEY_RIGHT_ROTATE):
            self.cam.roty += 4.
        elif self._is_in(key, self.KEY_TOP_ROTATE):
            self.cam.rotx += 4
        elif self._is_in(key, self.KEY_DOWN_ROTATE):
            self.cam.rotx -= 4

    @staticmethod
    def _is_in(buttons, keys):
        for k in keys:
            if buttons == k:
                return True
        return False


    def set_animation_speed(self, speed):
        " set speed between 0 and 100, where 10 is equals to a second"
        self.animation_speed = speed / 10

    def toggle_axis(self):
        self.show_axis = not self.show_axis

    def axis(self):
        """ Define vertices and colors for 3 planes
        """
        d = self.axis_factor
        vertices, colors = [], []
        #XZ RED
        vertices.extend([-d, 0, -d, d, 0, -d, d, 0, d, -d, 0, d])
        for i in range(4):
            colors.extend([1, 0, 0, 0.5])
        #YZ GREEN
        vertices.extend([0, -d, -d, 0, -d, d, 0, d, d, 0, d, -d])
        for i in range(4):
            colors.extend([0, 1, 0, 0.5])
        #XY BLUE
        vertices.extend([-d, -d, 0, d, -d, 0, d, d, 0, -d, d, 0])
        for i in range(4):
            colors.extend([0, 0, 1, 0.5])
        return gl_array(vertices), Color(np.array(colors))

    def draw_axis(self):
        """ Draw the 3 planes """
        vertices, colors = self.axis()
        glEnable(GL_DEPTH_TEST)
        draw_vertex_array(vertices, colors, GL_QUADS)
        glDisable(GL_DEPTH_TEST)

    def _draw_visualisation(self):
        if self.show_axis:
            self.draw_axis()

        selected_steps = [s for s in self._visualisation._steps if s.selected]
        n = len(selected_steps)
        if self.animation:
            n_visible = (time.time() % ((n+2)*self.animation_speed)) \
                        / self.animation_speed - 1
        else:
            n_visible = n
        for i, s in enumerate(selected_steps):
            if i < n_visible:
                s.draw()

    def toggle_animation(self):
        self.animation = not self.animation

    def speed_up(self):
        self.animation_speed += 1

    def speed_down(self):
        self.animation_speed -= 1


class Visualisation():
    def __init__(self, start_step=None):
        if start_step is None:
            start_step = Step()
        self._current_step = start_step
        self._steps = [self._current_step]

    def add(self, elem):
        self._current_step.add(elem)

    def point(self, point, color, size):
        self.add(Points(np.array([point]), color, size))

    def points(self, points, color):
        self.add(Points(points, color))

    def polygon(self, points, color):
        if points[1, :] != points[-1, :]:
            points = np.vstack((points, points[-1, :]))
        self.add(Polygons(np.array([points]), color))

    def next_step(self, step):
        self._current_step = step
        self._steps.append(step)

    def next(self, description):
        self._current_step = Step(description)
        self._steps.append(self._current_step)

    def show(self):
        app = QtCore.QCoreApplication.instance()
        if app is None:
            app = QtGui.QApplication(sys.argv)
        widget = VisualisationWidget(self)
        widget.show()
        app.exec_()


class ColorGroup:
    def __init__(self):
        self.n_groups = 0

    def next_member(self):
        self.n_groups += 1
        return ColorGroupMember(self, self.n_groups - 1)

    def get_color(self, index):
        h = index / self.n_groups
        s = 1
        v = 1
        r = 4
        alpha = index / ((1 - 1/r)*self.n_groups) + 1/r
        return colorsys.hsv_to_rgb(h, s, v) + (alpha, )


class ColorGroupMember:
    def __init__(self, color_group, i):
        self._color_group = color_group
        self._i = i

    def get_color(self):
        return self._color_group.get_color(self._i)


class Step:
    def __init__(self, description=""):
        self.description = description
        self._elems = []
        self.selected = True

    def add(self, elem):
        self._elems.append(elem)

    def draw(self):
        for elem in self._elems:
            elem.draw()

    def qtwidget(self):
        return QLabel(self.description)


class AnimationStep(object):
    def __init__(self):
        self.start = 0
        self.end = sys.maxsize

    def is_active(self, current_step):
        return self.start <= current_step <= self.end


class Polygons(AnimationStep):
    def __init__(self, polygons, colors=None, wireframe=None):
        """
            Add a polygon to the visualisation step.
            :param wireframe:
            :param polygons:  ndarray with a (n, m, 3)-shape, where n is the number
                              of polygons and m is the number of points of a polygon.
            :param colors:    ndarray with a (p, 4)-shape, where p is the total
                              number points. Each row represents a color
                              `[r, g, b, a]`.
            """
        super(Polygons, self).__init__()
        self._polygons = numpy2polygons(polygons)
        self._n_polygons, _, _ = self._polygons.shape
        self._colors = Color(colors)

    def draw(self):
        glLineWidth(1)
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glEnable(GL_DEPTH_TEST)
        for polygon in self._polygons:
            gl_polygon = gl_array(polygon.flatten().tolist())
            draw_vertex_array(gl_polygon, self._colors, GL_POLYGON)

        glDisable(GL_DEPTH_TEST)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)


class ConvexHulls(Polygons):
    pass


class RadonPartition(AnimationStep):
    # FIXME: generalise color from ColorGroup
    def __init__(self, smaller_points, bigger_points, radon_point, color):
        super(RadonPartition, self).__init__()
        self._smaller = smaller_points
        self._bigger = bigger_points
        self._radon_point = radon_point
        self._color = color

    def draw(self):
        color = self._color.get_color()
        ConvexHulls([self._smaller], color).draw()
        ConvexHulls([self._bigger], color).draw()
        draw_point(self._radon_point, color)


class PointGroups():
    def __init__(self):
        self._groups = []

    def new_group(self, points):
        self._groups.append(Points(points))
        for i, group in enumerate(self._groups):
            rgb = self.color(i)
            group.set_color(rgb)

    def draw(self):
        for group in self._groups:
            group.draw()

    def color(self, i):
        n = len(self._groups)
        h = i / n
        s = 1
        v = 1
        return colorsys.hsv_to_rgb(h, s, v) + (1, )  # set alpha


class Points(AnimationStep):
    def __init__(self, points, colors=None, size=1):
        super(Points, self).__init__()
        self._n_points, _ = points.shape
        self._points = points.astype(np.float32)
        self._colors = Color(colors)
        self._size = size

    def set_color(self, color):
        self._colors = Color(color)

    def draw(self):
        glPointSize(self._size)
        draw_vertex_array(gl_array(self._points.flatten().tolist()),
                          self._colors, GL_POINTS)
        glPointSize(1)


class Gui:
    def __init__(self):
        self.app = QtGui.QApplication(sys.argv)
        window = VisualisationController()
        window.show()

