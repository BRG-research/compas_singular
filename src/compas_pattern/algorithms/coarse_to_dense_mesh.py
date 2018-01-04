import math

from compas.datastructures.mesh import Mesh

from compas_pattern.topology.polyline_extraction import quad_mesh_polylines_all

from compas.geometry.algorithms.interpolation import discrete_coons_patch

from compas_pattern.topology.joining_welding import join_and_weld_meshes

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2017, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'


__all__ = [
    'quad_mesh_densification',
]

def quad_mesh_densification(mesh, target_length):
    """Densifies a quad mesh based on a target length.
    
    Parameters
    ----------
    mesh : Mesh
        The quad mesh to densify.
    target_length : float
        Target length for densification.

    Returns
    -------
    dense_mesh: Mesh, None
        Densified quad mesh.
        None if not a quad mesh.

    Raises
    ------
    -

    """

    if not mesh.is_quadmesh():
        return None

    # collect dual polyedges based on polyfaces
    polyfaces = quad_mesh_polylines_all(mesh, dual = True)
    dual_polyedges = []
    for polyface in polyfaces:
        dual_polyedge = []

        for i in range(len(polyface) - 1):
            u, v = mesh.face_adjacency_halfedge(polyface[i], polyface[i + 1])
            
            # first edge
            if i == 0 and polyface[0] != polyface[-1]:
                w = mesh.face_vertex_descendant(polyface[i], v)
                x = mesh.face_vertex_descendant(polyface[i], w)
                dual_polyedge.append([x, w])

            # regular edges
            dual_polyedge.append([u, v])
            
            # last edge
            if i == len(polyface) - 2 and polyface[0] != polyface[-1]:
                w = mesh.face_vertex_ancestor(polyface[i + 1], v)
                x = mesh.face_vertex_ancestor(polyface[i + 1], w)
                dual_polyedge.append([x, w])

        dual_polyedges.append(dual_polyedge)

    # determine subdivision parameter based on target length and dual edge average length
    group_subdivision = {}
    edge_group = {}

    for i, dual_polyedge in enumerate(dual_polyedges):

        average_length = 0
        for u, v in dual_polyedge:
            average_length += mesh.edge_length(u, v)
        average_length /= len(dual_polyedge)

        subdivision_parameter = math.ceil(average_length / target_length)
        group_subdivision[i] = subdivision_parameter

        for u, v in dual_polyedge:
            edge_group[(u, v)] = i
            edge_group[(v, u)] = i

    # mesh each patch
    meshes = []

    for fkey in mesh.faces():
        a, b, c, d = mesh.face_vertices(fkey)
        group_1 = edge_group[(a, b)]
        group_2 = edge_group[(b, c)]
        n = int(group_subdivision[group_1])
        m = int(group_subdivision[group_2])
        # subdivision points
        ab = [mesh.edge_point(a, b, float(i) / n) for i in range(0, n + 1)]
        bc = [mesh.edge_point(b, c, float(i) / m) for i in range(0, m + 1)]
        dc = [mesh.edge_point(d, c, float(i) / n) for i in range(0, n + 1)]
        ad = [mesh.edge_point(a, d, float(i) / n) for i in range(0, m + 1)]

        # create mesh
        vertices, face_vertices = discrete_coons_patch(ab, bc, dc, ad)
        face_mesh = Mesh.from_vertices_and_faces(vertices, face_vertices)
        meshes.append(face_mesh)

    dense_mesh = join_and_weld_meshes(meshes)

    return dense_mesh

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas