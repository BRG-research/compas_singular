import compas_rhino as rhino

from compas.datastructures.mesh import Mesh

import math

try:
    import rhinoscriptsyntax as rs

except ImportError:
    import platform
    if platform.python_implementation() == 'IronPython':
        raise

from compas_pattern.cad.rhino.editing_artist import apply_rule
from compas_pattern.topology.global_propagation import mesh_propagation

from compas.utilities import geometric_key

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2017, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'


__all__ = [
    'editing',
]

def editing(mesh):
    """Edit a mesh.

    Parameters
    ----------
    planar_mesh : Mesh
        A planar mesh to remap on the surface.
    spatial_surface : Rhino surface guid
        A spatial Rhino surface on which to remap the mesh.

    Returns
    -------
    mesh: Mesh
        The remapped mesh.

    Raises
    ------
    -

    """

    # temporary layer for visualisation
    rs.AddLayer('temp')

    # grammar rules
    rules_subdivide = ['simple_split', 'double_split', 'flat_corner_2', 'flat_corner_3', 'flat_corner_33', 'split_35', 'split_35_diag', 'split_26']
    rules_poles = ['face_pole', 'edge_pole', 'vertex_pole', 'insert_pole', 'insert_partial_pole']
    rules_strips = ['face_strip_collapse', 'face_strip_insert']
    rules_genus = ['add_opening', 'close_opening', 'add_handle', 'close_handle', 'close_handle_2']
    rules_others = ['singular_boundary_1', 'singular_boundary_2', 'singular_boundary_minus_1', 'rotate_vertex']
    rules_geometry = ['move_vertices', 'project_on_surface']
    
    rule_cluster = ['subdivide', 'poles', 'strips', 'genus', 'others', 'geometry', 'propagate']

    clusters = {'subdivide': rules_subdivide, 'poles': rules_poles, 'strips': rules_strips, 'genus': rules_genus, 'others': rules_others, 'geometry': rules_geometry}
    # regular vertices of initial mesh
    regular_vertices = list(mesh.vertices())

    # first visualisation
    rs.EnableRedraw(False)
    copy_mesh = mesh.to_mesh()
    edges = [rs.AddLine(copy_mesh.vertex_coordinates(u), copy_mesh.vertex_coordinates(v)) for u,v in copy_mesh.edges() if u != v and geometric_key(copy_mesh.vertex_coordinates(u)) != geometric_key(copy_mesh.vertex_coordinates(v))]
    rs.ObjectLayer(edges, 'temp')
    rs.EnableRedraw(True)
        
    # start editing
    count = 1000
    while count > 0:
        count -= 1

        #ask for rule
        cluster = rs.GetString('rule cluster?', strings = rule_cluster)
        rs.EnableRedraw(False)

        # intermediary propagation
        if cluster == 'propagate':
            mesh_propagation(mesh, regular_vertices)
            for vkey in mesh.vertices():
            # update regualr vertices
                regular = True
                for fkey in mesh.vertex_faces(vkey):
                    if len(mesh.face_vertices(fkey)) > 4:
                        regular = False
                        break
                if regular and vkey not in regular_vertices:
                    regular_vertices.append(vkey)

        
        # apply editing rule
        elif cluster in rule_cluster:
            if cluster in clusters.keys():
                rule = rs.GetString('rule?', strings = clusters[cluster])
                apply_rule(mesh, rule)

        # if nothing, check if mesh is valid after a final propagation
        else:
            # propapgate
            mesh_propagation(mesh, regular_vertices)
            rs.DeleteObjects(edges)
            rs.DeleteLayer('temp')
            break

        # update regular vertices
        for vkey in mesh.vertices():
            regular = True
            for fkey in mesh.vertex_faces(vkey):
                if len(mesh.face_vertices(fkey)) != 4:
                    regular = False
                    break
            if regular and vkey not in regular_vertices:
                regular_vertices.append(vkey)

        # update edges
        rs.EnableRedraw(False)
        rs.DeleteObjects(edges)
        copy_mesh = mesh.to_mesh()
        edges = [rs.AddLine(copy_mesh.vertex_coordinates(u), copy_mesh.vertex_coordinates(v)) for u,v in copy_mesh.edges() if u != v and geometric_key(copy_mesh.vertex_coordinates(u)) != geometric_key(copy_mesh.vertex_coordinates(v))]
        rs.ObjectLayer(edges, 'temp')
        rs.EnableRedraw(True)

    return mesh


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas
