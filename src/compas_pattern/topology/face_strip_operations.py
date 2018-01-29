from compas.datastructures.mesh import Mesh

from compas_pattern.topology.polyline_extraction import dual_edge_groups

from compas_pattern.topology.joining_welding import weld_mesh

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [
    'face_strip_collapse',
]


def face_strip_collapse(cls, mesh, u, v):
    """Collapse a face strip in a quad mesh.

    Parameters
    ----------
    mesh : Mesh
        A quad mesh.
    u: int
        Key of edge start vertex.
    v: int
        Key of edge end vertex.

    Returns
    -------
    mesh : mesh, None
        The modified quad mesh.
        None if mesh is not a quad mesh or if (u,v) is not an edge.

    Raises
    ------
    -

    """

    # checks
    if not mesh.is_quadmesh():
        return None
    if v not in mesh.halfedge[u] and u not in mesh.halfedge[v]:
        return None

    edge_groups, max_group = dual_edge_groups(mesh)
    group_number = edge_groups[(u, v)]
    edges_to_collapse = [edge for edge, group in edge_groups.items() if group == group_number]

    for u, v in edges_to_collapse:
        if v in mesh.halfedge[u]:
            fkey = mesh.halfedge[u][v]
            if fkey is not None:
                mesh.delete_face(fkey)

    boundary_vertices = mesh.vertices_on_boundary()
    print boundary_vertices
    for u, v in edges_to_collapse:
        if u in boundary_vertices and v not in boundary_vertices:
            x, y, z = mesh.vertex_coordinates(v)
        elif v in boundary_vertices and u not in boundary_vertices:
            x, y, z = mesh.vertex_coordinates(u)
        else:
            x, y, z = mesh.edge_midpoint(u, v)
        w = mesh.add_vertex(attr_dict = {'x': x, 'y': y, 'z': z})
        for vkey in [u, v]:
            for fkey in mesh.vertex_faces(vkey):
                face_vertices = mesh.face_vertices(fkey)[:]
                idx = face_vertices.index(vkey)
                face_vertices[idx] = w
                mesh.delete_face(fkey)
                mesh.add_face(face_vertices, fkey)

    mesh = weld_mesh(cls, mesh)

    return mesh

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas

