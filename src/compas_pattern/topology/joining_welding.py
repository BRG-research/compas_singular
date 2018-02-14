from compas.datastructures.mesh import Mesh

from compas.utilities import geometric_key

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2017, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'


__all__ = [
    'weld_mesh',
    'join_mesh',
    'join_and_weld_meshes',
]

def weld_mesh(cls, mesh, precision = '3f'):
    """Welds vertices of a mesh within some precision.

    Parameters
    ----------
    mesh : Mesh
        A mesh.

    precision: str
        Float precision of the geometric_key.

    Returns
    -------
    mesh : Mesh
        The welded mesh.

    Raises
    ------
    -

    """
    
    vertices = []
    face_vertices = []
    vertex_map = {}
    count = 0

    # store vertices from different geometric key only
    for vkey in mesh.vertices():
        xyz = mesh.vertex_coordinates(vkey)
        geom_key = geometric_key(xyz, precision)
        if geom_key not in vertex_map:
            vertex_map[geom_key] = count
            vertices.append(xyz)
            count += 1

    # update face vertices with index matching geometric key
    for fkey in mesh.faces():
        old_face_vertices = mesh.face_vertices(fkey)
        new_face_vertices = []
        for vkey in old_face_vertices:
            xyz = geometric_key(mesh.vertex_coordinates(vkey), precision)
            new_face_vertices.append(vertex_map[xyz])
        face_vertices.append(new_face_vertices)

    welded_mesh = cls.from_vertices_and_faces(vertices, face_vertices)

    return welded_mesh

def join_and_weld_meshes(cls, meshes, precision = '3f'):
    """Joins and welds vertices of meshes within some precision.

    Parameters
    ----------
    meshes : list
        A list of meshes.

    precision: str
        Float precision of the geometric_key.

    Returns
    -------
    mesh : Mesh
        The joined and welded mesh.

    Raises
    ------
    -

    """

    vertices = []
    face_vertices = []
    vertex_map = {}
    count = 0

    # store vertices from different geometric key only
    for mesh in meshes:
        for vkey in mesh.vertices():
            xyz = mesh.vertex_coordinates(vkey)
            geom_key = geometric_key(xyz, precision)
            if geom_key not in vertex_map:
                vertex_map[geom_key] = count
                vertices.append(xyz)
                count += 1

        # update face vertices with index matching geometric key
        for fkey in mesh.faces():
            old_face_vertices = mesh.face_vertices(fkey)
            new_face_vertices = []
            for vkey in old_face_vertices:
                xyz = geometric_key(mesh.vertex_coordinates(vkey), precision)
                new_face_vertices.append(vertex_map[xyz])
            face_vertices.append(new_face_vertices)

    joined_and_welded_mesh = cls.from_vertices_and_faces(vertices, face_vertices)

    return joined_and_welded_mesh

def join_meshes(cls, meshes):
    """Joins meshes without welding.

    Parameters
    ----------
    meshes : list
        A list of meshes.

    Returns
    -------
    mesh : Mesh
        The unwelded joined mesh.

    Raises
    ------
    -

    """

    vertices = []
    face_vertices = []

    # procede per mesh
    for mesh in meshes:
        # aggregate vertices
        remap_vertices = {}
        for vkey in mesh.vertices():
            idx = len(vertices)
            remap_vertices[vkey] = idx
            vertices.append(mesh.vertex_coordinates(vkey))
        for fkey in mesh.faces():
            face_vertices.append([remap_vertices[vkey] for vkey in mesh.face_vertices(fkey)])

    joined_mesh = cls.from_vertices_and_faces(vertices, face_vertices)

    return joined_mesh

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas
