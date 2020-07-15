from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

from compas_singular.datastructures import Mesh

from compas.geometry import delaunay_from_points

from compas.rpc import Proxy

from compas.geometry import is_point_in_polygon_xy
from compas.geometry import length_vector
from compas.geometry import subtract_vectors
from compas.geometry import cross_vectors

from compas.datastructures import trimesh_face_circle

from compas.datastructures import mesh_unweld_edges

from compas.utilities import pairwise
from compas.utilities import geometric_key

__all__ = [
    'delaunay_compas',
    'delaunay_numpy_rpc',
    'delaunay_numpy',
    'boundary_triangulation'
]


def delaunay_compas(vertices):
    """Delaunay triangulation from compas.

    Parameters
    ----------
    vertices : list
        List of vertex coordinates.

    Returns
    -------
    list
        List of face vertices.

    """

    return delaunay_from_points(vertices)


def delaunay_numpy_rpc(vertices):
    """RPC for Delaunay triangulation from numpy.

    Parameters
    ----------
    vertices : list
        List of vertex coordinates.

    Returns
    -------
    list
        List of face vertices.

    """

    geometry = Proxy('compas.geometry.triangulation.triangulation_numpy')
    return geometry.delaunay_from_points_numpy(vertices)


def delaunay_numpy(vertices):
    """Delaunay triangulation from numpy.

    Parameters
    ----------
    vertices : list
        List of vertex coordinates.

    Returns
    -------
    list
        List of face vertices.

    """

    from compas.geometry import delaunay_from_points_numpy
    return delaunay_from_points_numpy(vertices)


def boundary_triangulation(outer_boundary, inner_boundaries, polyline_features = [], point_features = [], delaunay=None):
    """Generate Delaunay triangulation between a planar outer boundary and planar inner boundaries. All vertices lie the boundaries.

    Parameters
    ----------
    outer_boundary : list
        Planar outer boundary as list of vertex coordinates.
    inner_boundaries : list
        List of planar inner boundaries as lists of vertex coordinates.
    polyline_features : list
        List of planar polyline_features as lists of vertex coordinates.
    point_features : list
        List of planar point_features as lists of vertex coordinates.
    delaunay : callable or proxy
        Delaunay triangulation function.

    Returns
    -------
    delaunay_mesh : Mesh
        The Delaunay mesh.

    """

    # generate planar Delaunay triangulation
    vertices = [pt for boundary in [outer_boundary] + inner_boundaries + polyline_features for pt in boundary] + point_features

    # if src == 'numpy_rpc':
    # 	faces = delaunay_numpy_rpc(vertices)
    # elif src == 'numpy':
    # 	faces = delaunay_numpy(vertices)
    # else:
    # 	faces = delaunay_compas(vertices)

    if not delaunay:
        delaunay = delaunay_compas

    faces = delaunay(vertices)

    delaunay_mesh = Mesh.from_vertices_and_faces(vertices, faces)

    # delete false faces with aligned vertices
    for fkey in list(delaunay_mesh.faces()):
        a, b, c = [delaunay_mesh.vertex_coordinates(vkey) for vkey in delaunay_mesh.face_vertices(fkey)]
        ab = subtract_vectors(b, a)
        ac = subtract_vectors(c, a)
        if length_vector(cross_vectors(ab, ac)) == 0:
            delaunay_mesh.delete_face(fkey)

    # delete faces outisde the borders
    for fkey in list(delaunay_mesh.faces()):
        centre = trimesh_face_circle(delaunay_mesh, fkey)[0]
        if not is_point_in_polygon_xy(centre, outer_boundary) or any([is_point_in_polygon_xy(centre, inner_boundary) for inner_boundary in inner_boundaries]):
            delaunay_mesh.delete_face(fkey)

    # topological cut along the feature polylines through unwelding
    vertex_map = {geometric_key(delaunay_mesh.vertex_coordinates(vkey)): vkey for vkey in delaunay_mesh.vertices()}
    edges = [edge for polyline in polyline_features for edge in pairwise([vertex_map[geometric_key(point)] for point in polyline])]
    mesh_unweld_edges(delaunay_mesh, edges)

    return delaunay_mesh


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas
