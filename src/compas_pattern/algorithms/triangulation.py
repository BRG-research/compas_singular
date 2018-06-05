from compas.datastructures.mesh import Mesh

from compas.topology import delaunay_from_points

from compas.utilities import geometric_key

from compas_pattern.topology.unwelding import unweld_mesh_along_edge_path

from compas_pattern.datastructures.mesh import face_circle

import random

from compas.geometry import centroid_points
from compas.geometry import distance_point_point
from compas.geometry import add_vectors
from compas.geometry import bounding_box

from compas.geometry import is_point_in_polygon_xy
from compas.geometry import is_point_in_triangle_xy
from compas.geometry import is_point_in_circle_xy
from compas.geometry import circle_from_points_xy

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2017, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'


__all__ = [
    'triangulation',
    'delaunay_from_points_2'
]

def triangulation(boundary, holes = [], polyline_features = [], point_features = []):
    """Generates a trimmed Delaunay mesh on a closed outer boundary polyline with potential
    closed inner boundary polylines, polyline constraints and point constraints.

    Parameters
    ----------
    boundary : list
        List of vertices of the closed outer boundary polyline.
    holes : list
        List of lists of vertices of the closed inner boundary polylines.
    polyline_features : list
        List of lists of vertices of the feature polylines for constraints to the Delaunay triangulation.
    point_features : list
        List of points for constraints to the Delaunay triangulation.

    Returns
    -------
    delunay_mesh: Mesh

    Raises
    ------
    -

    """

    # get polyline points for Delaunay triangulation
    delaunay_points = []
    delaunay_points += boundary + point_features
    for polyline in holes:
        delaunay_points += polyline
    for polyline in polyline_features:
        delaunay_points += polyline

    # remove duplicates based on their geometric keys
    delaunay_point_map = {}
    for point in delaunay_points:
        geom_key = geometric_key(point)
        if geom_key not in delaunay_point_map:
            delaunay_point_map[geom_key] = point
    delaunay_points = list(delaunay_point_map.values())

    holes = [hole[: -1] for hole in holes]
    
    # generate Delaunay mesh
    delaunay_faces = delaunay_from_points_2(delaunay_points, boundary = boundary[: -1], holes = holes)
    delaunay_mesh = Mesh.from_vertices_and_faces(delaunay_points, delaunay_faces)

    # topological cut along the feature polylines through unwelding
    vertex_map = {geometric_key(delaunay_mesh.vertex_coordinates(vkey)): vkey for vkey in delaunay_mesh.vertices()}

    edge_paths = []
    for polyline in polyline_features:
        edge_path = []
        vertex_path = [vertex_map[geometric_key(point)] for point in polyline]
        for i in range(len(vertex_path) - 1):
            if vertex_path[i + 1] in delaunay_mesh.halfedge[vertex_path[i]]:
                edge_path.append([vertex_path[i], vertex_path[i + 1]])
        edge_paths.append(edge_path)

    for edge_path in edge_paths:
        unweld_mesh_along_edge_path(delaunay_mesh, edge_path)

    return delaunay_mesh

def delaunay_from_points_2(points, boundary=None, holes=None, tiny=1e-12):
    """Computes the delaunay triangulation for a list of points.
    Difference from compas version: faces outside the boundaries are detected based on the position of their circumcircle.

    Parameters
    ----------
    points : sequence of tuple
        XYZ coordinates of the original points.
    boundary : sequence of tuples
        list of ordered points describing the outer boundary (optional)
    holes : list of sequences of tuples
        list of polygons (ordered points describing internal holes (optional)

    Returns
    -------
    list
        The faces of the triangulation.
        Each face is a triplet of indices referring to the list of point coordinates.

    Notes
    -----
    For more info, see [1]_.

    References
    ----------
    .. [1] Sloan, S. W., 1987 *A fast algorithm for constructing Delaunay triangulations in the plane*
           Advances in Engineering Software 9(1): 34-55, 1978.

    Example
    -------
    .. plot::
        :include-source:

        from compas.geometry import pointcloud_xy
        from compas.datastructures import Mesh
        from compas.topology import delaunay_from_points
        from compas.plotters import MeshPlotter

        points = pointcloud_xy(10, (0, 10))
        faces = delaunay_from_points(points)

        delaunay = Mesh.from_vertices_and_faces(points, faces)

        plotter = MeshPlotter(delaunay)

        plotter.draw_vertices(radius=0.1)
        plotter.draw_faces()

        plotter.show()

    """
    from compas.datastructures import Mesh

    def super_triangle(coords):
        centpt = centroid_points(coords)
        bbpts  = bounding_box(coords)
        dis    = distance_point_point(bbpts[0], bbpts[2])
        dis    = dis * 300
        v1     = (0 * dis, 2 * dis, 0)
        v2     = (1.73205 * dis, -1.0000000000001 * dis, 0)  # due to numerical issues
        v3     = (-1.73205 * dis, -1 * dis, 0)
        pt1    = add_vectors(centpt, v1)
        pt2    = add_vectors(centpt, v2)
        pt3    = add_vectors(centpt, v3)
        return pt1, pt2, pt3

    mesh = Mesh()

    # to avoid numerical issues for perfectly structured point sets
    points = [(point[0] + random.uniform(-tiny, tiny), point[1] + random.uniform(-tiny, tiny), 0.0) for point in points]

    # create super triangle
    pt1, pt2, pt3 = super_triangle(points)

    # add super triangle vertices to mesh
    n = len(points)
    super_keys = n, n + 1, n + 2

    mesh.add_vertex(super_keys[0], {'x': pt1[0], 'y': pt1[1], 'z': pt1[2]})
    mesh.add_vertex(super_keys[1], {'x': pt2[0], 'y': pt2[1], 'z': pt2[2]})
    mesh.add_vertex(super_keys[2], {'x': pt3[0], 'y': pt3[1], 'z': pt3[2]})

    mesh.add_face(super_keys)

    # iterate over points
    for i, pt in enumerate(points):
        key = i

        # newtris should be intialised here

        # check in which triangle this point falls
        for fkey in list(mesh.faces()):
            # abc = mesh.face_coordinates(fkey) #This is slower
            # This is faster:
            keya, keyb, keyc = mesh.face_vertices(fkey)

            dicta = mesh.vertex[keya]
            dictb = mesh.vertex[keyb]
            dictc = mesh.vertex[keyc]

            a = [dicta['x'], dicta['y']]
            b = [dictb['x'], dictb['y']]
            c = [dictc['x'], dictc['y']]

            if is_point_in_triangle_xy(pt, [a, b, c], True):
                # generate 3 new triangles (faces) and delete surrounding triangle
                key, newtris = mesh.insert_vertex(fkey, key=key, xyz=pt, return_fkeys=True)
                break

        while newtris:
            fkey = newtris.pop()

            # get opposite_face
            keys  = mesh.face_vertices(fkey)
            s     = list(set(keys) - set([key]))
            u, v  = s[0], s[1]
            fkey1 = mesh.halfedge[u][v]

            if fkey1 != fkey:
                fkey_op, u, v = fkey1, u, v
            else:
                fkey_op, u, v = mesh.halfedge[v][u], u, v

            if fkey_op:
                keya, keyb, keyc = mesh.face_vertices(fkey_op)
                dicta = mesh.vertex[keya]
                a = [dicta['x'], dicta['y']]
                dictb = mesh.vertex[keyb]
                b = [dictb['x'], dictb['y']]
                dictc = mesh.vertex[keyc]
                c = [dictc['x'], dictc['y']]

                circle = circle_from_points_xy(a, b, c)

                if is_point_in_circle_xy(pt, circle):
                    fkey, fkey_op = mesh.swap_edge_tri(u, v)
                    newtris.append(fkey)
                    newtris.append(fkey_op)

    # Delete faces adjacent to supertriangle
    for key in super_keys:
        mesh.delete_vertex(key)

    # Delete faces outside of boundary
    if boundary:
        for fkey in list(mesh.faces()):
            #centroid = mesh.face_centroid(fkey)
            centre, radius, normal = face_circle(mesh, fkey)
            if not is_point_in_polygon_xy(centre, boundary):
                mesh.delete_face(fkey)

    # Delete faces inside of inside boundaries
    if holes:
        for polygon in holes:
            for fkey in list(mesh.faces()):
                #centroid = mesh.face_centroid(fkey)
                centre, radius, normal = face_circle(mesh, fkey)
                if is_point_in_polygon_xy(centre, polygon):
                    mesh.delete_face(fkey)

    return [mesh.face_vertices(fkey) for fkey in mesh.faces()]

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas
