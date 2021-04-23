from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from math import pi
from math import cos
from math import sin
from math import atan

from compas.geometry import distance_point_point
from compas.geometry import add_vectors
from compas.geometry import scale_vector
from compas.geometry import length_vector
from compas.geometry import dot_vectors
from compas.geometry import subtract_vectors
from compas.utilities import pairwise


__all__ = [
    'closest_point_on_circle',
    'closest_point_on_line',
    'closest_point_on_segment',
    'closest_point_on_polyline',
    'closest_point_on_polylines'
]


def closest_point_on_circle(x0, y0, r):
    """Project point (x0, y0) onto circle with centre at (0, 0) and radius r.

    Parameters
    ----------
    x0: float
        Point x coordinate.
    y0: float
        Point y coordinate.
    r: float
        Circle radius.

    Returns
    -------
    [x, y] : list
        The xy coordinates of the projected point.
    """

    if x0 == 0.0 and y0 == 0.0:
        return r, 0.0

    if x0 == 0:
        theta = abs(y0) / y0 * pi / 2.0
    else:
        theta = atan(y0 / x0)

    x = r * cos(theta)
    y = r * sin(theta)

    if x0 < 0:
        x *= -1
        y *= -1

    return [x, y]


def closest_point_on_line(a, b, c):
    """Closest point on line.
    Same as projection.

    Parameters
    ----------
    a: list
        First line point coordinates.
    b: list
        Second line point coordinates.
    c: list
        Point coordinates.

    Returns
    -------
    tuple
        The projected point coordinates and the distance from the input point.
    """

    ab = subtract_vectors(b, a)
    ac = subtract_vectors(c, a)

    if length_vector(ab) == 0:
        return a, distance_point_point(c, a)

    p = add_vectors(a, scale_vector(ab, dot_vectors(ab, ac) / length_vector(ab) ** 2))
    distance = distance_point_point(c, p)
    return p, distance


def closest_point_on_segment(a, b, c):
    """Closest point on segment.
    Different from projection because an extremity is yielded if the projection is on the line but outside the segment.

    Parameters
    ----------
    a: list
        First line point coordinates.
    b: list
        Second line point coordinates.
    c: list
        Point coordinates.

    Returns
    -------
    tuple
        The projected point coordinates and the distance from the input point.
    """

    p, distance = closest_point_on_line(a, b, c)

    ab = subtract_vectors(b, a)
    ap = subtract_vectors(p, a)

    if dot_vectors(ab, ap) < 0:
        return a, distance_point_point(c, a)
    elif length_vector(ab) < length_vector(ap):
        return b, distance_point_point(c, b)
    else:
        return p, distance


def closest_point_on_polyline(polyline, c):
    """Closest point on polyline.
    If there are multiple closest points, the one from the first polyline segment is yielded.

    Parameters
    ----------
    polyline: list
        List of polyline point coordinates.
    p: list
        Point coordinates.

    Returns
    -------
    tuple
        The projected point coordinates and the distance from the input point.
    """

    proj_p = None
    min_distance = None
    for a, b in pairwise(polyline):
        p, distance = closest_point_on_segment(a, b, c)
        if proj_p is None or min_distance > distance:
            proj_p = p
            min_distance = distance
    return proj_p, min_distance


def closest_point_on_polylines(polylines, p):
    """Closest point on polylines.
    If there are multiple closest points, the one from the first polyline segment is yielded.

    Parameters
    ----------
    polylines: list
        List of polylines as lists of point coordinates.
    p: list
        Point coordinates.

    Returns
    -------
    tuple
        The projected point coordinates and the distance from the input point.
    """

    proj_p = None
    min_distance = None
    for polyline in polylines:
        proj_p, distance = closest_point_on_polyline(polyline, p)
        if proj_p is None or min_distance > distance:
            proj_p = p
            min_distance = distance
    return proj_p, min_distance


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':
    pass
