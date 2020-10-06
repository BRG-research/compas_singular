from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

# from math import pi
# from math import cos
# from math import sin
# from math import tan

import rhinoscriptsyntax as rs

from compas.geometry import cross_vectors
from compas.geometry import scale_vector
from compas.geometry import add_vectors
from compas.geometry import normalize_vector
from compas.geometry import subtract_vectors
from compas.geometry import midpoint_line
# from compas.geometry import distance_point_point
# from compas.geometry import bounding_box
# from compas.datastructures import mesh_weld

# import compas_rhino as rhino


__all__ = [
    'draw_graph'
]


def draw_graph(vertices, edges, loop_size=1.0, spindle_size=1.0, node_radius=0.0, line_radius=0.0, key_to_colour={}):
    """Draw a graph in Rhino as grouped points and lines with optional element size and node colouring.
    Loops for edges (u, u) and parallel edges for multiple edges (u, v) and/or (v, u) are allowed.

    Parameters
    ----------
    vertices : dict
        A dictionary of vertex keys pointing to point coordinates.
    edges : list
        A list of tuples of pairs of vertex indices.
    loop_size : float, optional
        Rough size of the loops due to edges (u, u).
        Default value is 1.0.
    spindle_size : float, optional
        Rough size of the spindles due to mutiple edges (u, v) and/or (v, u).
        Default value is 1.0.
    node_radius : float, optional
        Node radius representing the vertices. If equal to 0.0, a point is added, else a sphere.
        Default value is 1.0.
    line_radius : float, optional
        Line radius representing the edges. If equal to 0.0, a line is added, else a pipe.
        Default value is 1.0.
    key_to_colour : dict, optional
        An optional dictonary with vertex keys pointing to RGB colours.

    Returns
    -------
    group : Rhino group
        A Rhino group with the list of points or sphere surfaces of the vertices, and the list of the list of curves or pipe surfaces of the edges.
    """

    # nodes as points or spheres with optional colours
    nodes = []
    for key, xyz in vertices.items():
        nodes.append(rs.AddPoint(xyz) if node_radius == 0.0 else rs.AddSphere(xyz, node_radius))
        if key in key_to_colour:
            rs.ObjectColor(nodes[-1], key_to_colour[key])

    # curves
    curves = []
    while len(edges) > 0:
        crvs = []
        u0, v0 = edges.pop()
        # count occurences in case of multiple parallel edges
        n = 1
        for u, v in edges:
            if (u == u0 and v == v0) or (u == v0 and v == u0):
                edges.remove((u, v))
                n += 1
        # if not loop edge
        if u0 != v0:
            start = vertices[u0]
            end = vertices[v0]
            # rough spindle of parallel edges based on third offset point
            mid = midpoint_line([start, end])
            direction = cross_vectors(normalize_vector(subtract_vectors(end, start)), [0.0, 0.0, 1.0])
            for i in range(n):
                k = (float(i) / float(n) * spindle_size) - spindle_size / 2.0 * (float(n) - 1.0) / float(n)
                dir_mid = add_vectors(mid, scale_vector(direction, k))
                crvs.append(rs.AddInterpCurve([start, dir_mid, end], degree=3))

        # if loop edge
        else:
            xyz0 = vertices[u0]
            x0, y0, z0 = xyz0
            # rough loop based on three additional points
            xyz1 = [x0 + loop_size / 2.0, y0 - loop_size / 2.0, z0]
            xyz2 = [x0 + loop_size, y0, z0]
            xyz3 = [x0 + loop_size / 2.0, y0 + loop_size / 2.0, z0]
            crvs += [rs.AddInterpCurve([xyz0, xyz1, xyz2, xyz3, xyz0], degree=3) for i in range(n)]
            # spread if multiple loops
            for i, crv in enumerate(crvs):
                rs.RotateObject(crv, [x0, y0, z0], 360 * float(i) / float(n))

        # pipe if non-null radius is specified
        if line_radius != 0.0:
            pipes = [rs.AddPipe(crv, 0, line_radius) for crv in crvs]
            rs.DeleteObjects(crvs)
            crvs = pipes

        curves += crvs

    # output group
    group = rs.AddGroup()
    rs.AddObjectsToGroup(nodes + curves, group)
    return group


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':
    pass
