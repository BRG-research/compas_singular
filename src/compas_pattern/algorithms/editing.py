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

    # grammar rules + propagation scheme
    rules = ['face_pole', 'edge_pole', 'vertex_pole', 'face_opening', 'flat_corner_2', 'flat_corner_3', 'flat_corner_33', 'split_35', 'split_35_diag', 'split_26', 'simple_split', 'double_split', 'insert_pole', 'insert_partial_pole', 'singular_boundary_1', 'singular_boundary_2', 'face_strip_collapse', 'face_strip_insert', 'rotate_vertex', 'clear_faces', 'add_handle', 'propagate', 'move_vertices', 'exit']
    
    # regular vertices of initial mesh
    regular_vertices = list(mesh.vertices())

    # first visualisation
    rs.EnableRedraw(False)
    edges = [rs.AddLine(mesh.vertex_coordinates(u), mesh.vertex_coordinates(v)) for u,v in mesh.edges() if u != v and geometric_key(mesh.vertex_coordinates(u)) != geometric_key(mesh.vertex_coordinates(v))]
    rs.ObjectLayer(edges, 'temp')
    rs.EnableRedraw(True)
        
    # start editing
    count = 1000
    while count > 0:
        count -= 1

        #ask for rule
        rule = rs.GetString('rule?', strings = rules)
        rs.EnableRedraw(False)
        
        # exit
        if rule == 'exit':
            # propapgate
            mesh_propagation(mesh, regular_vertices)
            rs.DeleteObjects(edges)
            rs.DeleteLayer('temp')
            break

        # intermediary propagation
        elif rule == 'propagate':
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
        elif rule in rules:
            apply_rule(mesh, rule)

        # if nothing, check if mesh is valid after a final propagation
        else:
            # propapgate
            mesh_propagation(mesh, regular_vertices)
            # check validity
            valid = True
            for fkey in mesh.faces():
                if len(mesh.face_vertices(fkey)) > 4:
                    valid = False
            if valid:
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
        edges = [rs.AddLine(mesh.vertex_coordinates(u), mesh.vertex_coordinates(v)) for u, v in mesh.edges() if mesh.vertex_coordinates(u) != mesh.vertex_coordinates(v)]
        rs.ObjectLayer(edges, 'temp')
        rs.EnableRedraw(True)

    return mesh


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas
