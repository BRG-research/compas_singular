import math

from compas.datastructures.mesh import Mesh

from compas_pattern.topology.polyline_extraction import quad_mesh_polylines_all
from compas_pattern.topology.polyline_extraction import dual_edge_groups

from compas.geometry.algorithms.interpolation import discrete_coons_patch

from compas_pattern.topology.joining_welding import join_and_weld_meshes

from compas_pattern.datastructures.pseudo_quad_mesh import PseudoQuadMesh

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

    # # collect dual polyedges based on polyfaces
    # polyfaces = quad_mesh_polylines_all(mesh, dual = True)

    # dual_polyedges = []
    # for polyface in polyfaces:
    #     dual_polyedge = []

    #     for i in range(len(polyface) - 1):
    #         u, v = mesh.face_adjacency_halfedge(polyface[i], polyface[i + 1])
            
    #         # first edge
    #         if i == 0 and polyface[0] != polyface[-1]:
    #             w = mesh.face_vertex_descendant(polyface[i], v)
    #             x = mesh.face_vertex_descendant(polyface[i], w)
    #             dual_polyedge.append([x, w])

    #         # regular edges
    #         dual_polyedge.append([u, v])
            
    #         # last edge
    #         if i == len(polyface) - 2 and polyface[0] != polyface[-1]:
    #             w = mesh.face_vertex_ancestor(polyface[i + 1], v)
    #             x = mesh.face_vertex_ancestor(polyface[i + 1], w)
    #             dual_polyedge.append([x, w])

    #     dual_polyedges.append(dual_polyedge)

    edge_groups, max_group = dual_edge_groups(mesh)

    dual_polyedges = []
    for i in range(max_group + 1):
        dual_polyedge = []
        for u, v in edge_groups:
            if edge_groups[(u, v)] == i:
                if (v, u) not in dual_polyedge:
                    dual_polyedge.append(([u, v]))
        if len(dual_polyedge) > 0:
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
        # exceptions if pseudo quad face with a (u, u) edge in no groups
        if (a, b) in edge_group: 
            group_1 = edge_group[(a, b)]
        else:
            group_1 = edge_group[(c, d)]
        if (b, c) in edge_group:
            group_2 = edge_group[(b, c)]
        else:
            group_2 = edge_group[(d, a)]
        n = int(group_subdivision[group_1])
        m = int(group_subdivision[group_2])
        # subdivision points
        ab = [mesh.edge_point(a, b, float(i) / n) for i in range(0, n + 1)]
        bc = [mesh.edge_point(b, c, float(i) / m) for i in range(0, m + 1)]
        dc = [mesh.edge_point(d, c, float(i) / n) for i in range(0, n + 1)]
        ad = [mesh.edge_point(a, d, float(i) / n) for i in range(0, m + 1)]

        # create mesh
        vertices, face_vertices = discrete_coons_patch(ab, bc, dc, ad)
        face_mesh = PseudoQuadMesh.from_vertices_and_faces(vertices, face_vertices)
        meshes.append(face_mesh)

    dense_mesh = join_and_weld_meshes(PseudoQuadMesh, meshes)

    # remove pseudo quads: [a, b, c, c] -> [a, b, c]
    for fkey in dense_mesh.faces():
        to_change = False
        face_vertices = dense_mesh.face_vertices(fkey)
        new_face_vertices = []
        for vkey in face_vertices:
            if len(new_face_vertices) == 0 or vkey != new_face_vertices[-1]:
                new_face_vertices.append(vkey)
            else:
                to_change = True
        if new_face_vertices[0] == new_face_vertices[-1]:
            del new_face_vertices[-1]
            to_change = True
        if to_change:
            dense_mesh.delete_face(fkey)
            dense_mesh.add_face(new_face_vertices, fkey)

    

    # unweld along two-sided openings

    return dense_mesh

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas