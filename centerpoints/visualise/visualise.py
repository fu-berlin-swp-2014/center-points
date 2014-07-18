import time
import colorsys
import sys

from PySide import QtGui, QtOpenGL, QtCore
from PySide.QtCore import QTimer, SIGNAL
from PySide.QtGui import QLabel
import numpy as np

import OpenGL
from OpenGL.GL import *
from OpenGL.GLU import *



def playground():
    """ Draw something here, like a white X.
    glColor4f(1, 1, 1, 1)
    glBegin(GL_LINES)
    glVertex3f(0, 0, 0)
    glVertex3f(640, 480, 0)

    glVertex3f(0, 0, 0)
    glVertex3f(640, -480, 0)

    glVertex3f(0, 480, 0)
    glVertex3f(640, 0, 0)
    glEnd()

    glBegin(GL_POINTS)
    glVertex3f(100, 100, 100)
    glEnd()
    """


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
    KEY_FARER = [QtCore.Qt.Key_W, QtCore.Qt.Key_Plus]
    KEY_NEARER = [QtCore.Qt.Key_S, QtCore.Qt.Key_Minus]

    KEY_DOWN_ROTATE = [QtCore.Qt.Key_Down]
    KEY_TOP_ROTATE = [QtCore.Qt.Key_Up]
    KEY_LEFT_ROTATE = [QtCore.Qt.Key_Left]
    KEY_RIGHT_ROTATE = [QtCore.Qt.Key_Right]

    PROJECTIVE = 2
    ISOMETRIC = 1

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
        if self.mode == 1:
            return
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


class VisualisationWindow(QtGui.QWidget):
    def __init__(self, visualisation, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self._glWidget = GLWidget(visualisation)
        self._stepsWidget = QtGui.QVBoxLayout()
        self._visualisation = visualisation
        mainLayout = QtGui.QHBoxLayout()
        # mainLayout.addLayout(self._stepsWidget)
        mainLayout.addWidget(self._glWidget)
        self.setLayout(mainLayout)
        self.setWindowTitle(self.tr("Hello GL"))

    def refreshSteps(self):
        for i, s in enumerate(self._visualisation._steps):
            if s.description is None:
                s.description = "Step: " + str(i)
            self._stepsWidget.addWidget(s.qtwidget())


class GLWidget(QtOpenGL.QGLWidget):
    def __init__(self, visualisation, parent=None, cam=None, fps=30):
        QtOpenGL.QGLWidget.__init__(self, parent)
        if cam is None:
            cam = Camera()

        self.cam = cam
        self.visualisation = visualisation
        self.initOpenGL()
        self.lastPos = QtCore.QPoint()
        self.timer = QTimer()
        self.connect(self.timer, SIGNAL("timeout()"), self.updateGL)
        self.timer.start()
        self.timer.setInterval(1000 / fps)

    def initOpenGL(self):
        """ Initial OpenGL configuration. """
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDepthFunc(GL_LEQUAL)

    def paintGL(self):
        print("paint!!")
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.cam.apply()
        self.visualisation.draw()

    def repaint(self, *args, **kwargs):
        self.paintGL()

    def resizeGL(self, width, height):
        self.cam.set_size(width, height)

    def mousePressEvent(self, event):
        self.lastPos = QtCore.QPoint(event.pos())

    def mouseMoveEvent(self, event):
        dx = event.x() - self.lastPos.x()
        dy = event.y() - self.lastPos.y()
        print("dx: " + str(dx))
        if event.buttons() & QtCore.Qt.LeftButton:
            self.cam.rotx += dy
            self.cam.roty += dx
        elif event.buttons() & QtCore.Qt.RightButton:
            self.cam.rotx += 8 * dy
            self.cam.roty += 8 * dx

        self.lastPos = QtCore.QPoint(event.pos())

    def keyPressEvent(self, event):
        bottons = event.buttons()
        print("press event: " + event.text())

        if bottons & QtCore.Qt.KEY_P:
            self.cam.perspective()
        elif bottons & QtCore.Qt.KEY_I:
            self.isometric()
        elif self.cam.mode == self.PROJECTIVE \
                and self._is_in(bottons, self.KEY_FARER):
            self.cam.fov -= 3
            self.cam.update_projection()
        elif self.cam.mode == self.PROJECTIVE \
                and self._is_in(bottons, self.KEY_NEARER):
            self.cam.fov += 3
            self.cam.perspective()
        elif self._is_in(bottons, self.KEY_LEFT_ROTATE):
            self.roty -= 4.
        elif self._is_in(bottons, self.KEY_RIGHT_ROTATE):
            self.roty += 4.
        elif self._is_in(bottons, self.KEY_TOP_ROTATE):
            self.rotx += 4
        elif self._is_in(bottons, self.KEY_DOWN_ROTATE):
            self.rotx -= 4

    @staticmethod
    def _is_in(buttons, keys):
        for k in keys:
            if buttons & k:
                return True
        return False


class Visualisation():
    def __init__(self):
        self.display_axis = True

        self.app = QtGui.QApplication(sys.argv)
        self.window = VisualisationWindow(self)
        self._current_step = Step()
        self._steps = [self._current_step]
        self.steps_delay = 1
        self.axis_factor = 100
        self._start_time = time.time()
        self.duration = 10

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

    def draw(self):
        self.draw_axis()
        for s in self._steps:
            s.draw()

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

    def next_step(self, step=None):
        if step is None:
            step = Step()

        self._current_step = step
        self._steps.append(step)

    def show(self):
        # self.window.refreshSteps()
        self.window.show()
        self.app.exec_()


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
        self.visible = False

    def add(self, elem):
        self._elems.append(elem)

    def draw(self):
        for elem in self._elems:
            elem.draw()

    def qtwidget(self):
        label = QLabel()
        label.setText(self.description)



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
            print(str(gl_polygon[0]))
            print(self._colors._color)
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
