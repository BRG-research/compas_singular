from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

__all__ = [
    'mesh_move_vertex_by',
    'mesh_move_by',
    'mesh_move_vertices_by',
    'mesh_move_vertex_to',
    'mesh_move_vertices_to'
]


def mesh_move_vertex_by(mesh, vector, vkey):
    """Move a mesh vertex by a vector.

    Parameters
    ----------
    mesh : Mesh
        A mesh.
    vector : list
        An XYZ vector.
    vkey : hashable
        A vertex key.
    """

    mesh.vertex[vkey]['x'] += vector[0]
    mesh.vertex[vkey]['y'] += vector[1]
    mesh.vertex[vkey]['z'] += vector[2]


def mesh_move_by(mesh, vector):
    """Move a mesh by a vector.

    Parameters
    ----------
    mesh : Mesh
        A mesh.
    vector : list
        An XYZ vector.
    """

    for vkey in mesh.vertices():
        mesh_move_vertex_by(mesh, vector, vkey)


def mesh_move_vertices_by(mesh, key_to_vector):
    """Move mesh vertices by different vectors.

    Parameters
    ----------
    mesh : Mesh
        A mesh.
    key_to_vector : dict
        A dictionary of vertex keys pointing to vectors.
    """

    for vkey, vector in key_to_vector.items():
        mesh_move_vertex_by(mesh, vector, vkey)


def mesh_move_vertex_to(mesh, point, vkey):
    """Move a mesh vertex to a point.

    Parameters
    ----------
    mesh : Mesh
        A mesh.
    point : list
        An XYZ point.
    vkey : hashable
        A vertex key.
    """

    mesh.vertex[vkey]['x'] = point[0]
    mesh.vertex[vkey]['y'] = point[1]
    mesh.vertex[vkey]['z'] = point[2]


def mesh_move_vertices_to(mesh, key_to_point):
    """Move mesh vertices to different points.

    Parameters
    ----------
    mesh : Mesh
        A mesh.
    key_to_point : dict
        A dictionary of vertex keys pointing to points.
    """

    for vkey, point in key_to_point.items():
        mesh_move_vertex_to(mesh, point, vkey)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':
    pass
