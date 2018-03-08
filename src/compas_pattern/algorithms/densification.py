import math

try:
    import rhinoscriptsyntax as rs

except ImportError:
    import platform
    if platform.python_implementation() == 'IronPython':
        raise

from compas.datastructures.mesh import Mesh

from compas_pattern.topology.polyline_extraction import dual_edge_polylines

from compas.geometry.algorithms.interpolation import discrete_coons_patch

from compas_pattern.topology.joining_welding import join_and_weld_meshes

from compas_pattern.datastructures.pseudo_quad_mesh import PseudoQuadMesh

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2017, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'


__all__ = [
    'densification',
]

def densification(mesh, target_length):
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

    edge_groups, max_group = dual_edge_polylines(mesh)

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

    # propose customization of local density
    count = 100
    while count > 0:
        count -= 1
        rs.EnableRedraw(False)
        all_dots = []
        for dual_polyedge in dual_polyedges:
            u0, v0 = dual_polyedge[0]
            group = edge_group[(u0, v0)]
            parameter = group_subdivision[group]
            dots = []
            for u, v in dual_polyedge:
                if u > v:
                    continue
                point = mesh.edge_midpoint(u, v)
                group = edge_group[(u, v)]
                parameter = int(group_subdivision[group])
                dots.append(rs.AddTextDot(parameter, point))
            k = float(group) / float(max_group) * 255
            RGB = [k] * 3
            rs.AddGroup(group)
            rs.ObjectColor(dots, RGB)
            rs.AddObjectsToGroup(dots, group)
            all_dots += dots
        rs.EnableRedraw(True)
        dot = rs.GetObject('edge group to modify', filter = 8192)
        if dot is not None:
            group = int(rs.ObjectGroups(dot)[0])
            parameter = rs.GetInteger('subdivision parameter', number = 3, minimum = 1)
            group_subdivision[group] = parameter
        rs.EnableRedraw(False)
        rs.DeleteObjects(all_dots)
        rs.EnableRedraw(True)
        if dot is None:
            break

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