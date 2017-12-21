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


def weld_mesh(mesh, precision = '3f'):
    """Weld vertices of a mesh within some precision.

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

    welded_mesh = Mesh.from_vertices_and_faces(vertices, face_vertices)
    return welded_mesh


def join_and_weld_meshes(meshes, precision = '3f'):
    """Weld vertices of a mesh within some precision.

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

    joined_and_welded_mesh = Mesh.from_vertices_and_faces(vertices, face_vertices)
    return joined_and_welded_mesh


def join_meshes(meshes):
    """Join meshes without welding.

    Parameters
    ----------
    meshes : list
        A list of meshes.

    Returns
    -------
    mesh : Mesh
        The joined mesh.

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

    joined_mesh = Mesh.from_vertices_and_faces(vertices, face_vertices)

    return joined_mesh


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas

    vertices_0 = [[0.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 2.0, 0.0], [0.0, 3.0, 0.0], [0.0, 4.0, 0.0], [0.0, 5.0, 0.0], [1.0, 0.0, 0.0], [1.0, 1.0, 0.0], [1.0, 2.0, 0.0], [1.0, 3.0, 0.0], [1.0, 4.0, 0.0], [1.0, 5.0, 0.0], [2.0, 0.0, 0.0], [2.0, 1.0, 0.0], [2.0, 2.0, 0.0], [2.0, 3.0, 0.0], [2.0, 4.0, 0.0], [2.0, 5.0, 0.0], [3.0, 0.0, 0.0], [3.0, 1.0, 0.0], [3.0, 2.0, 0.0], [3.0, 3.0, 0.0], [3.0, 4.0, 0.0], [3.0, 5.0, 0.0], [4.0, 0.0, 0.0], [4.0, 1.0, 0.0], [4.0, 2.0, 0.0], [4.0, 3.0, 0.0], [4.0, 4.0, 0.0], [4.0, 5.0, 0.0], [5.0, 0.0, 0.0], [5.0, 1.0, 0.0], [5.0, 2.0, 0.0], [5.0, 3.0, 0.0], [5.0, 4.0, 0.0], [5.0, 5.0, 0.0], [5.0, 0.0, 0.0], [5.0, 1.0, 0.0], [5.0, 2.0, 0.0], [5.0, 3.0, 0.0], [5.0, 4.0, 0.0], [5.0, 5.0, 0.0], [6.0, 0.0, 0.0], [6.0, 1.0, 0.0], [6.0, 2.0, 0.0], [6.0, 3.0, 0.0], [6.0, 4.0, 0.0], [6.0, 5.0, 0.0], [7.0, 0.0, 0.0], [7.0, 1.0, 0.0], [7.0, 2.0, 0.0], [7.0, 3.0, 0.0], [7.0, 4.0, 0.0], [7.0, 5.0, 0.0], [8.0, 0.0, 0.0], [8.0, 1.0, 0.0], [8.0, 2.0, 0.0], [8.0, 3.0, 0.0], [8.0, 4.0, 0.0], [8.0, 5.0, 0.0], [9.0, 0.0, 0.0], [9.0, 1.0, 0.0], [9.0, 2.0, 0.0], [9.0, 3.0, 0.0], [9.0, 4.0, 0.0], [9.0, 5.0, 0.0], [10.0, 0.0, 0.0], [10.0, 1.0, 0.0], [10.0, 2.0, 0.0], [10.0, 3.0, 0.0], [10.0, 4.0, 0.0], [10.0, 5.0, 0.0]]
    face_vertices_0 = [[7, 1, 0, 6], [8, 2, 1, 7], [9, 3, 2, 8], [10, 4, 3, 9], [11, 5, 4, 10], [13, 7, 6, 12], [14, 8, 7, 13], [15, 9, 8, 14], [16, 10, 9, 15], [17, 11, 10, 16], [19, 13, 12, 18], [20, 14, 13, 19], [21, 15, 14, 20], [22, 16, 15, 21], [23, 17, 16, 22], [25, 19, 18, 24], [26, 20, 19, 25], [27, 21, 20, 26], [28, 22, 21, 27], [29, 23, 22, 28], [31, 25, 24, 30], [32, 26, 25, 31], [33, 27, 26, 32], [34, 28, 27, 33], [35, 29, 28, 34], [43, 37, 36, 42], [44, 38, 37, 43], [45, 39, 38, 44], [46, 40, 39, 45], [47, 41, 40, 46], [49, 43, 42, 48], [50, 44, 43, 49], [51, 45, 44, 50], [52, 46, 45, 51], [53, 47, 46, 52], [55, 49, 48, 54], [56, 50, 49, 55], [57, 51, 50, 56], [58, 52, 51, 57], [59, 53, 52, 58], [61, 55, 54, 60], [62, 56, 55, 61], [63, 57, 56, 62], [64, 58, 57, 63], [65, 59, 58, 64], [67, 61, 60, 66], [68, 62, 61, 67], [69, 63, 62, 68], [70, 64, 63, 69], [71, 65, 64, 70]]
    mesh_0 = Mesh.from_vertices_and_faces(vertices_0, face_vertices_0)

    vertices_1 = [[0.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 2.0, 0.0], [0.0, 3.0, 0.0], [0.0, 4.0, 0.0], [0.0, 5.0, 0.0], [1.0, 0.0, 0.0], [1.0, 1.0, 0.0], [1.0, 2.0, 0.0], [1.0, 3.0, 0.0], [1.0, 4.0, 0.0], [1.0, 5.0, 0.0], [2.0, 0.0, 0.0], [2.0, 1.0, 0.0], [2.0, 2.0, 0.0], [2.0, 3.0, 0.0], [2.0, 4.0, 0.0], [2.0, 5.0, 0.0], [3.0, 0.0, 0.0], [3.0, 1.0, 0.0], [3.0, 2.0, 0.0], [3.0, 3.0, 0.0], [3.0, 4.0, 0.0], [3.0, 5.0, 0.0], [4.0, 0.0, 0.0], [4.0, 1.0, 0.0], [4.0, 2.0, 0.0], [4.0, 3.0, 0.0], [4.0, 4.0, 0.0], [4.0, 5.0, 0.0], [5.0, 0.0, 0.0], [5.0, 1.0, 0.0], [5.0, 2.0, 0.0], [5.0, 3.0, 0.0], [5.0, 4.0, 0.0], [5.0, 5.0, 0.0]]
    face_vertices_1 = [[7, 1, 0, 6], [8, 2, 1, 7], [9, 3, 2, 8], [10, 4, 3, 9], [11, 5, 4, 10], [13, 7, 6, 12], [14, 8, 7, 13], [15, 9, 8, 14], [16, 10, 9, 15], [17, 11, 10, 16], [19, 13, 12, 18], [20, 14, 13, 19], [21, 15, 14, 20], [22, 16, 15, 21], [23, 17, 16, 22], [25, 19, 18, 24], [26, 20, 19, 25], [27, 21, 20, 26], [28, 22, 21, 27], [29, 23, 22, 28], [31, 25, 24, 30], [32, 26, 25, 31], [33, 27, 26, 32], [34, 28, 27, 33], [35, 29, 28, 34]]
    mesh_1 = Mesh.from_vertices_and_faces(vertices_1, face_vertices_1)

    vertices_2 = [[5.0, 0.0, 0.0], [5.0, 1.0, 0.0], [5.0, 2.0, 0.0], [5.0, 3.0, 0.0], [5.0, 4.0, 0.0], [5.0, 5.0, 0.0], [6.0, 0.0, 0.0], [6.0, 1.0, 0.0], [6.0, 2.0, 0.0], [6.0, 3.0, 0.0], [6.0, 4.0, 0.0], [6.0, 5.0, 0.0], [7.0, 0.0, 0.0], [7.0, 1.0, 0.0], [7.0, 2.0, 0.0], [7.0, 3.0, 0.0], [7.0, 4.0, 0.0], [7.0, 5.0, 0.0], [8.0, 0.0, 0.0], [8.0, 1.0, 0.0], [8.0, 2.0, 0.0], [8.0, 3.0, 0.0], [8.0, 4.0, 0.0], [8.0, 5.0, 0.0], [9.0, 0.0, 0.0], [9.0, 1.0, 0.0], [9.0, 2.0, 0.0], [9.0, 3.0, 0.0], [9.0, 4.0, 0.0], [9.0, 5.0, 0.0], [10.0, 0.0, 0.0], [10.0, 1.0, 0.0], [10.0, 2.0, 0.0], [10.0, 3.0, 0.0], [10.0, 4.0, 0.0], [10.0, 5.0, 0.0]]
    face_vertices_2 = [[7, 1, 0, 6], [8, 2, 1, 7], [9, 3, 2, 8], [10, 4, 3, 9], [11, 5, 4, 10], [13, 7, 6, 12], [14, 8, 7, 13], [15, 9, 8, 14], [16, 10, 9, 15], [17, 11, 10, 16], [19, 13, 12, 18], [20, 14, 13, 19], [21, 15, 14, 20], [22, 16, 15, 21], [23, 17, 16, 22], [25, 19, 18, 24], [26, 20, 19, 25], [27, 21, 20, 26], [28, 22, 21, 27], [29, 23, 22, 28], [31, 25, 24, 30], [32, 26, 25, 31], [33, 27, 26, 32], [34, 28, 27, 33], [35, 29, 28, 34]]
    mesh_2 = Mesh.from_vertices_and_faces(vertices_2, face_vertices_2)

    print mesh_0
    print weld_mesh(mesh_0)

    print mesh_1
    print mesh_2
    print join_meshes([mesh_1, mesh_2])
    print join_and_weld_meshes([mesh_1, mesh_2])