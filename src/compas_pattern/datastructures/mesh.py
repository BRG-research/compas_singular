from compas.datastructures.mesh import Mesh

from compas.geometry import circle_from_points

from compas.topology import mesh_unify_cycles


from compas_pattern.topology.polyline_extraction import mesh_boundaries

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2017, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [
    'mesh_topology',
    'mesh_area',
    'mesh_centroid',
    'mesh_normal',
    'add_vertex_from_vertices',
    'insert_vertices_in_halfedge',
    'face_point',
    'face_circle',
    'insert_vertex_in_face',
    'insert_vertices_in_face',
    'delete_face',
    'mesh_disjointed_parts',
]

def mesh_topology(mesh):

    V = mesh.number_of_vertices()
    E = mesh.number_of_edges()
    F = mesh.number_of_faces()
    B = len(mesh_boundaries(mesh))
    X = V - E + F
    G = (2 - X - B) / 2

    return V, E, F, B, X, G

def mesh_area(mesh):

    area = sum([mesh.face_area(fkey) for fkey in mesh.faces()])

    return area
    
def mesh_centroid(mesh):

    centroid = [0, 0, 0]
    for fkey in mesh.faces():
        x, y, z = mesh.face_centroid(fkey)
        area = mesh.face_area(fkey)
        centroid[0] += area * x
        centroid[1] += area * y
        centroid[2] += area * z
    centroid = [xyz / n for xyz, n in zip(centroid, [mesh_area(mesh)] * 3)]  

    return centroid

def mesh_normal(mesh):

    normal = [0, 0, 0]
    for fkey in mesh.faces():
        x, y, z = mesh.face_normal(fkey)
        area = mesh.face_area(fkey)
        normal[0] += area * x
        normal[1] += area * y
        normal[2] += area * z
    normal = [xyz / n for xyz, n in zip(normal, [len(normal)] * 3)]  

    return normal

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

    centre, radius, normal = circle_from_points(a, b, c)
    
    return centre, radius, normal

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

def mesh_disjointed_parts(mesh):
    # cycles must be unified or mesh_unify_cycles(mesh) must be extended to disjointed meshes

    faces = list(mesh.faces())

    disjointed_parts = []

    count = len(faces)
    while len(faces) > 0 and count > 0:
        count -= 1
        part = [faces.pop()]
        next_neighbours = [part[-1]]
        count_2  = count
        while len(next_neighbours) > 0 and count_2 > 0:
            count_2 -= 1
            for fkey in mesh.face_neighbours(next_neighbours.pop()):
                if fkey not in part:
                    part.append(fkey)
                    faces.remove(fkey)
                    if fkey not in next_neighbours:
                        next_neighbours.append(fkey)
        disjointed_parts.append(part)

    return disjointed_parts

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas