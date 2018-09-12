from compas.datastructures.mesh import Mesh

from compas.utilities import geometric_key

from compas_pattern.datastructures.mesh import mesh_disjointed_parts

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2017, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'


__all__ = [
    'weld_mesh',
    'join_meshes',
    'join_and_weld_meshes',
    'unweld_mesh_along_edge_path',
    'unjoin_mesh_parts',
]

def weld_mesh(mesh, tolerance = '3f'):
    """Weld vertices of a mesh.

    Parameters
    ----------
    mesh : Mesh
        A mesh.

    tolerance: str
        Tolerance for welding.

    Returns
    -------
    vertices : list
        The vertices of the new mesh.
    faces : list
        The faces of the new mesh.

    """
    
    vertices = []
    vertex_map = {}
    index = 0
    # store and map vertices with the same geometric keys to the same new index
    for vkey in mesh.vertices():
        xyz = mesh.vertex_coordinates(vkey)
        geom_key = geometric_key(xyz, tolerance)
        if geom_key not in vertex_map:
            vertex_map[geom_key] = index
            vertices.append(xyz)
            index += 1

    # change indices in the face vertices
    faces = [ [vertex_map[geometric_key(mesh.vertex_coordinates(vkey), tolerance)] for vkey in mesh.face_vertices(fkey)] for fkey in mesh.faces()]

    return vertices, faces

def join_and_weld_meshes(meshes, tolerance = '3f'):
    """Join and and weld meshes.

    Parameters
    ----------
    meshes : list
        A list of meshes.

    tolerance: str
        Tolerance for welding.

    Returns
    -------
    vertices : list
        The vertices of the new mesh.
    faces : list
        The faces of the new mesh.

    """

    vertices = []
    vertex_map = {}
    index = 0
    faces = []

    # store and map vertices with the same geometric keys to the same new index
    for mesh in meshes:
        for vkey in mesh.vertices():
            xyz = mesh.vertex_coordinates(vkey)
            geom_key = geometric_key(xyz, tolerance)
            if geom_key not in vertex_map:
                vertex_map[geom_key] = index
                vertices.append(xyz)
                index += 1

        # change indices in the face vertices
        faces += [ [vertex_map[geometric_key(mesh.vertex_coordinates(vkey), tolerance)] for vkey in mesh.face_vertices(fkey)] for fkey in mesh.faces()]

    return vertices, faces

def join_meshes(meshes):
    """Join meshes without welding.

    Parameters
    ----------
    meshes : list
        A list of meshes.

    Returns
    -------
    vertices : list
        The vertices of the new mesh.
    faces : list
        The faces of the new mesh.

    """

    vertices = []
    index = 0
    faces = []

    for mesh in meshes:
        vertex_map = {}
        for vkey in mesh.vertices():
            vertex_map[vkey] = index
            index += 1
            vertices.append(mesh.vertex_coordinates(vkey))
        for fkey in mesh.faces():
            faces.append([vertex_map[vkey] for vkey in mesh.face_vertices(fkey)])

    return vertices, faces

def unweld_mesh_along_edge_path(mesh, edge_path):
    """Unwelds a mesh along an edge path.

    Parameters
    ----------
    mesh : Mesh
    edge_path: list
        Edge path for unwelding.

    Returns
    -------
    mesh : Mesh
        The unwelded mesh.

    """
    
    duplicates = []

    # convert edge path in vertex path
    vertex_path = [edge[0] for edge in edge_path]
    # add last vertex of edge path only if not closed loop
    if edge_path[0][0] != edge_path[-1][-1]:
        vertex_path.append(edge_path[-1][-1])

    # store changes to make in the faces along the vertex path in the following format {face to change = [old vertex, new vertex]}
    to_change = {}

    # iterate along path
    for i, vkey in enumerate(vertex_path):
        # vertices before and after current
        last_vkey = vertex_path[i - 1]
        next_vkey = vertex_path[i + 1 - len(vertex_path)]

        # skip the extremities of the vertex path, except if the path is a loop or if vertex is on boundary
        if (edge_path[0][0] == edge_path[-1][-1]) or (i != 0 and i != len(vertex_path) - 1) or mesh.is_vertex_on_boundary(vkey):
            # duplicate vertex and its attributes
            attr = mesh.vertex[vkey]
            new_vkey = mesh.add_vertex(attr_dict = attr)
            duplicates.append([vkey, new_vkey])
            # split neighbours in two groups depending on the side of the path
            vertex_nbrs = mesh.vertex_neighbors(vkey, True)
            
            # two exceptions on last_vkey or next_vkey if the vertex is on the boundary or a non-manifold vertex in case of the last vertex of a closed edge path
            if edge_path[0][0] == edge_path[-1][-1] and i == len(vertex_path) - 1:
                next_vkey = vertex_path[0]
            if mesh.is_vertex_on_boundary(vkey):
                for j in range(len(vertex_nbrs)):
                    if mesh.is_vertex_on_boundary(vertex_nbrs[j - 1]) and mesh.is_vertex_on_boundary(vertex_nbrs[j]):
                        before, after = vertex_nbrs[j - 1], vertex_nbrs[j]
                if i == 0:
                    last_vkey = before
                elif i == len(vertex_path) - 1:
                    next_vkey = after

            idxa = vertex_nbrs.index(last_vkey)
            idxb = vertex_nbrs.index(next_vkey)
            if idxa < idxb:
                half_nbrs = vertex_nbrs[idxa : idxb]
            else:
                half_nbrs = vertex_nbrs[idxa :] + vertex_nbrs[: idxb]
            
            # get faces corresponding to vertex neighbours
            faces = [mesh.halfedge[nbr][vkey] for nbr in half_nbrs]
            # store change per face with index of duplicate vertex
            for fkey in faces:
                if fkey in to_change:
                    # add to other changes
                    to_change[fkey] += [[vkey, new_vkey]]
                else: 
                    to_change[fkey] = [[vkey, new_vkey]]

    # apply stored changes
    for fkey, changes in to_change.items():
        if fkey is None:
            continue
        face_vertices = mesh.face_vertices(fkey)[:]
        for change in changes:
            old_vertex, new_vertex = change
            # replace in list of face vertices
            idx = face_vertices.index(old_vertex)
            face_vertices[idx] = new_vertex
        # modify face by removing it and adding the new one
        attr = mesh.facedata[fkey]
        mesh.delete_face(fkey)
        mesh.add_face(face_vertices, fkey, attr_dict = attr)

    return duplicates

def unjoin_mesh_parts(mesh, parts):
    """Explode the parts of a mesh.

    Parameters
    ----------
    mesh : Mesh
        A mesh.
    parts : list
        List of lists of face keys.


    Returns
    -------
    meshes : list
        The unjoined meshes.

    """

    meshes = []
    for part in parts:
        vertices_keys = list(set([vkey for fkey in part for vkey in mesh.face_vertices(fkey)]))
        vertices = [mesh.vertex_coordinates(vkey) for vkey in vertices_keys]
        key_to_index = {vkey: i for i, vkey in enumerate(vertices_keys)}
        faces = [ [key_to_index[vkey] for vkey in mesh.face_vertices(fkey)] for fkey in part]
        meshes.append(Mesh.from_vertices_and_faces(vertices, faces))

    return meshes

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas
