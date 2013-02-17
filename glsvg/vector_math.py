from parser_utils import *
from OpenGL.GL import *
import math

EPSILON = 0.001


class vec2(object):
    def __init__(self, *args):
        if isinstance(args[0], vec2):
            self.x = args[0].x
            self.y = args[0].y
        elif isinstance(args[0], list):
            self.x, self.y = args[0]
        else:
            self.x, self.y = args[0], args[1]

    def __repr__(self):
        return '(' + str(self.x) + ',' + str(self.y) + ')'

    def __neg__(self):
        return vec2(-self.x, -self.y)

    def __abs__(self):
        return self.length()

    def __add__(self, other):
        return vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return vec2(self.x - other.x, self.y - other.y)

    def __mul__(self, scale):
        return vec2(self.x * scale, self.y * scale)

    def __div__(self, scale):
        return vec2(self.x / scale, self.y / scale)

    def __eq__(self, other):
        if not other: return False
        return abs(self.x - other.x) < EPSILON and abs(self.y - other.y) < EPSILON

    def __ne__(self, other):
        return not(self.__eq__(other))

    def normalized(self):
        l = self.length()
        if l == 0:
            return vec2(1, 0)
        else:
            return vec2(self.x, self.y) / self.length()

    def length(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)


def intersection(p1, p2, p3, p4):
    """
    Returns whether two lines intersected, and the point at which
    they intersected (or, "None" if the lines are parallel)
    """
    A1 = p2.y - p1.y
    B1 = p1.x - p2.x
    C1 = A1 * p1.x + B1 * p1.y

    A2 = p4.y - p3.y
    B2 = p3.x - p4.x
    C2 = A2 * p3.x + B2 * p3.y

    det = A1 * B2 - A2 * B1

    if abs(det) < EPSILON:  # Lines are parallel
        return False, None
    else:
        result = vec2(
            (B2 * C1 - B1 * C2) / det,
            (A1 * C2 - A2 * C1) / det)

    epsilon = .01

    on_line_segment = True
    on_line_segment &= result.x >= (min(p1.x, p2.x) - epsilon)
    on_line_segment &= result.y >= (min(p1.y, p2.y) - epsilon)
    on_line_segment &= result.x <= (max(p1.x, p2.x) + epsilon)
    on_line_segment &= result.y <= (max(p1.y, p2.y) + epsilon)

    return on_line_segment, result


def line_length(a, b):
    return math.sqrt((b.x - a.x) ** 2 + (b.y - a.y) ** 2)


def radian(deg):
    return deg * (math.pi / 180.0)

ninety_degrees = radian(90)


class Matrix(object):
    def __init__(self, string=None):
        self.values = [1, 0, 0, 1, 0, 0]
        if isinstance(string, str):
            string = string.strip()
            if string.startswith('matrix('):
                self.values = [float(x) for x in parse_list(string[7:-1])]
            elif string.startswith('translate('):
                x, y = [float(x) for x in parse_list(string[10:-1])]
                self.values = [1, 0, 0, 1, x, y]
            elif string.startswith('scale('):
                sx, sy = [float(x) for x in parse_list(string[6:-1])]
                self.values = [sx, 0, 0, sy, 0, 0]           
        elif string is not None:
            self.values = list(string)

    def __enter__(self):
        glPushMatrix()
        glMultMatrixf(self.to_mat4())
        return self

    def __exit__(self, type, value, traceback):
        glPopMatrix()

    def __call__(self, other):
        return (self.values[0] * other[0] + self.values[2] * other[1] + self.values[4],
                self.values[1] * other[0] + self.values[3] * other[1] + self.values[5])
    
    def __str__(self):
        return str(self.values)
    
    def to_mat4(self):
        v = self.values
        return [v[0], v[1], 0.0, 0.0,
                v[2], v[3], 0.0, 0.0,
                0.0,  0.0,  1.0, 0.0,
                v[4], v[5], 0.0, 1.0]
    
    def inverse(self):
        d = float(self.values[0] * self.values[3] - self.values[1] * self.values[2])
        return Matrix([self.values[3] / d, -self.values[1] / d, -self.values[2] / d, self.values[0] / d,
                       (self.values[2] * self.values[5] - self.values[3] * self.values[4]) / d,
                       (self.values[1] * self.values[4] - self.values[0] * self.values[5]) / d])

    def __mul__(self, other):
        a, b, c, d, e, f = self.values
        u, v, w, x, y, z = other.values
        return Matrix([
            a * u + c * v,
            b * u + d * v,
            a * w + c * x,
            b * w + d * x,
            a * y + c * z + e,
            b * y + d * z + f])


def svg_matrix_to_gl_matrix(matrix):
    v = matrix.values
    return [v[0], v[1], 0.0, v[2], v[3], 0.0, v[4], v[5], 1.0]