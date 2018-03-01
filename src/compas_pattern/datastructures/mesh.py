from compas.datastructures.mesh import Mesh

from compas.geometry import circle_from_points

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2017, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [
    'add_vertex_from_vertices',
    'insert_vertices_in_halfedge',
    'face_point',
    'face_circle',
    'insert_vertex_in_face',
    'insert_vertices_in_face',
    'delete_face',
]

def add_vertex_from_vertices(mesh, vertices, weights):
    n = len(vertices)
    if len(weights) != n:
        weights = [1] * n
    x, y, z = 0, 0, 0
    for i, vkey in enumerate(vertices):
        xyz = mesh.vertex_coordinates(vkey)
        x += xyz[0] * weights[i]
        y += xyz[1] * weights[i]
        z += xyz[2] * weights[i]
    sum_weights = sum(weights)
    x /= sum_weights
    y /= sum_weights
    z /= sum_weights

    return mesh.add_vertex(attr_dict = {'x': x, 'y': y, 'z': z})

def insert_vertices_in_halfedge(mesh, u, v, vertices):
    if v in mesh.halfedge[u] and mesh.halfedge[u][v] is not None:
        fkey = mesh.halfedge[u][v]
        return insert_vertices_in_face(mesh, fkey, u, vertices)
    else:
        return 0

def face_point(mesh, vertices, weights):
    n = len(vertices)
    if len(weights) != n:
        weights = [1] * n
    x, y, z = 0, 0, 0
    for i, vkey in enumerate(vertices):
        xyz = mesh.vertex_coordinates(vkey)
        x += xyz[0] * weights[i]
        y += xyz[1] * weights[i]
        z += xyz[2] * weights[i]
    sum_weights = sum(weights)
    x /= sum_weights
    y /= sum_weights
    z /= sum_weights
    return x, y, z

def face_circle(mesh, fkey):

    face_vertices = mesh.face_vertices(fkey)
    if len(face_vertices) != 3:
        return None
    
    a, b, c = face_vertices
    a = mesh.vertex_coordinates(a)
    b = mesh.vertex_coordinates(b)
    c = mesh.vertex_coordinates(c)

    center, radius, normal = circle_from_points(a, b, c)
    
    return center, radius, normal

def insert_vertex_in_face(mesh, fkey, vkey, added_vkey):
    """Insert a vertex in the vertices of a face after a vertex.

    Parameters
    ----------
    mesh : Mesh
        A mesh.
    fkey: int
        Face key.
    vkey: int
        Vertex key to insert.
    added_vkey: int
        Vertex key to insert after the existing vertex.

    Returns
    -------
    face_vertices: list or None
        New list of face vertices.
        None if vkey is not a vertex of the face.

    Raises
    ------
    -

    """

    if vkey not in mesh.face_vertices(fkey):
        return None

    face_vertices = mesh.face_vertices(fkey)[:]
    idx = face_vertices.index(vkey) + 1 - len(face_vertices)
    face_vertices.insert(idx, added_vkey)
    mesh.delete_face(fkey)
    mesh.add_face(face_vertices, fkey = fkey)

    return face_vertices

def insert_vertices_in_face(mesh, fkey, vkey, added_vkeys):
    """Insert vertices in the vertices of a face after a vertex.

    Parameters
    ----------
    mesh : Mesh
        A mesh.
    fkey: int
        Face key.
    vkeys: int
        Vertex key to insert.
    added_vkey: list
        List of vertex keys to insert after the existing vertex.

    Returns
    -------
    face_vertices: list or None
        New list of face vertices.
        None if vkey is not a vertex of the face.

    Raises
    ------
    -

    """

    if vkey not in mesh.face_vertices(fkey):
        return None

    face_vertices = mesh.face_vertices(fkey)[:]
    for added_vkey in reversed(added_vkeys):
        idx = face_vertices.index(vkey) + 1 - len(face_vertices)
        face_vertices.insert(idx, added_vkey)
    mesh.delete_face(fkey)
    mesh.add_face(face_vertices, fkey = fkey)

    return face_vertices

def delete_face(mesh, fkey):
    """Delete a face from the mesh object.

    Parameters
    ----------
    fkey : hashable
        The identifier of the face.

    Examples
    --------
    .. plot::
        :include-source:

        import compas
        from compas.datastructures import Mesh
        from compas.plotters import MeshPlotter

        mesh = Mesh.from_obj(compas.get('faces.obj'))

        mesh.delete_face(12)

        plotter = MeshPlotter(mesh)
        plotter.draw_vertices()
        plotter.draw_faces()
        plotter.show()

    """
    for u, v in mesh.face_halfedges(fkey):
        mesh.halfedge[u][v] = None
        if u in mesh.halfedge[v] and mesh.halfedge[v][u] is None:
            del mesh.halfedge[u][v]
            del mesh.halfedge[v][u]
    del mesh.face[fkey]

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas