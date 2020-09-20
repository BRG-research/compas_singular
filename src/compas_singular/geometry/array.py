from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from math import pi
from compas.geometry import circle_evaluate
from compas.geometry import archimedean_spiral_evaluate
from compas.geometry import add_vectors


__all__ = [
    'line_array',
    'rectangular_array',
    'circular_array',
    'spiral_array'
]


def line_array(n, d, anchor=[0.0, 0.0, 0.0]):
    return [add_vectors(anchor, [i * d, 0.0, 0.0]) for i in range(n)]


def rectangular_array(nx, ny, dx, dy, anchor=[0.0, 0.0, 0.0]):
    return [add_vectors(anchor, [x * dx, y * dy, 0.0]) for y in range(ny) for x in range(nx)]


def circular_array(n, r, anchor=[0.0, 0.0, 0.0]):
    return [add_vectors(anchor, circle_evaluate(2 * pi * float(i) / float(n), r)) for i in range(n)]


def spiral_array(n, d, anchor=[0.0, 0.0, 0.0]):
    # spiral parameters set to respect d spacing between consecutive points and consecutive spiral elements
    a, b = 0, d / (2 * pi)
    ts = [pi * b]
    for i in range(n):
        ts.append((2 * d / b + ts[-1] ** 2) ** .5)
    return [add_vectors(anchor, archimedean_spiral_evaluate(t, a, b, 0)) for t in ts]


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':
    pass

    # print(rectangular_array(4, 2, 10.0, 0.5, anchor=[1.0, -1.0, 0.0]))
    # print(spiral_array(15, 2, anchor=[1.0, -1.0, 0.0]))
