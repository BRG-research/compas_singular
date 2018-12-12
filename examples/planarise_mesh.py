import rhinoscriptsyntax as rs

import compas_rhino as rhino

from compas.datastructures.mesh import Mesh
from compas_pattern.datastructures.pseudo_quad_mesh import PseudoQuadMesh
from compas_pattern.datastructures.pseudo_quad_mesh import pqm_from_mesh
from compas_pattern.cad.rhino.utilities import draw_mesh


from compas.geometry import project_points_plane
from compas.geometry import centroid_points

from compas.geometry import distance_point_point
from compas.geometry import distance_line_line

from compas.geometry.algorithms.bestfit import bestfit_plane


def planarize_faces(vertices,
                    faces,
                    fixed=None,
                    kmax=100,
                    callback=None,
                    callback_args=None):
    """Planarise a set of connected faces.

    Planarisation is implemented as a two-step iterative procedure. At every
    iteration, faces are first individually projected to their best-fit plane,
    and then the vertices are projected to the centroid of the disconnected
    corners of the faces.

    Parameters
    ----------
    vertices : list
        The vertex coordinates.
    faces : list
        The vertex indices per face.
    fixed : list, optional [None]
        A list of fixed vertices.
    kmax : int, optional [100]
        The number of iterations.
    callback : callable, optional [None]
        A user-defined callback that is called after every iteration.
    callback_args : list, optional [None]
        A list of arguments to be passed to the callback function.

    See Also
    --------
    * :func:`compas.geometry.mesh_planarize_faces`
    * :func:`compas.geometry.mesh_planarize_faces_shapeop`

    """
    if callback:
        if not callable(callback):
            raise Exception('The callback is not callable.')

    fixed = fixed or []
    fixed = set(fixed)

    for k in range(kmax):

        positions = [[] for _ in range(len(vertices))]

        for face in iter(faces):
            points = [vertices[index] for index in face]
            plane = bestfit_plane(points)
            projections = project_points_plane(points, plane)

            for i, index in enumerate(face):
                positions[index].append(projections[i])

        for index, vertex in enumerate(vertices):
            if index in fixed:
                continue

            x, y, z = centroid_points(positions[index])
            vertex[0] = x
            vertex[1] = y
            vertex[2] = z

        if callback:
            callback(k, callback_args)
    
    return vertices



guid = rs.GetObject('get mesh')
mesh = rhino.mesh_from_guid(PseudoQuadMesh, guid)

vertices = []
key_to_index = {}
for i, vkey in enumerate(mesh.vertices()):
    vertices.append(mesh.vertex_coordinates(vkey))
    key_to_index[vkey] = i
faces = [[key_to_index[vkey] for vkey in mesh.face_vertices(fkey)] for fkey in fkeys]

fixed_vertices = [key_to_index[vkey] for vkey in mesh.vertices_on_boundary()]



new_vertices = planarize_faces(vertices, faces, fixed = fixed_vertices, kmax=100)


draw_mesh(Mesh.from_vertices_and_faces(new_vertices, faces))