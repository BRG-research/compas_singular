try:
    import rhinoscriptsyntax as rs

except ImportError:
    import platform
    if platform.python_implementation() == 'IronPython':
        raise

import compas_rhino as rhino

from compas.datastructures.mesh import Mesh

from compas_pattern.topology.grammar import face_pole
from compas_pattern.topology.grammar import edge_pole
from compas_pattern.topology.grammar import vertex_pole
from compas_pattern.topology.grammar import face_opening
from compas_pattern.topology.grammar import flat_corner_2
from compas_pattern.topology.grammar import flat_corner_3
from compas_pattern.topology.grammar import flat_corner_33
from compas_pattern.topology.grammar import split_35
from compas_pattern.topology.grammar import split_26
from compas_pattern.topology.grammar import simple_split
from compas_pattern.topology.grammar import double_split
from compas_pattern.topology.grammar import insert_pole
from compas_pattern.topology.grammar import insert_partial_pole

from compas_pattern.topology.polyline_extraction import dual_edge_polylines

from compas_pattern.topology.face_strip_operations import face_strip_collapse
from compas_pattern.topology.face_strip_operations import face_strip_insert

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2017, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'


__all__ = [
    'apply_rule',
]


def apply_rule(mesh, rule):
    
    if rule == 'face_pole':
        artist = rhino.MeshArtist(mesh, layer='mesh_artist')
        artist.clear_layer()
        
        artist.draw_facelabels()
        artist.redraw()
        fkey = rhino.mesh_select_face(mesh, message = 'fkey')
        artist.clear_layer()
        artist.redraw()
        
        rs.DeleteLayer('mesh_artist')
        
        face_pole(mesh, fkey)
    
    if rule == 'edge_pole':
        artist = rhino.MeshArtist(mesh, layer='mesh_artist')
        artist.clear_layer()
        
        artist.draw_facelabels()
        artist.redraw()
        fkey = rhino.mesh_select_face(mesh, message = 'fkey')
        artist.clear_layer()
        artist.redraw()
        
        artist.draw_edgelabels(text = {(u, v): "{}-{}".format(u, v) for u, v in mesh.face_halfedges(fkey)})
        artist.redraw()
        edge = rhino.mesh_select_edge(mesh, message = 'edge')
        artist.clear_layer()
        artist.redraw()
        
        rs.DeleteLayer('mesh_artist')
        
        edge_pole(mesh, fkey, edge)
    
    if rule == 'vertex_pole':
        artist = rhino.MeshArtist(mesh, layer='mesh_artist')
        artist.clear_layer()
        
        artist.draw_facelabels()
        artist.redraw()
        fkey = rhino.mesh_select_face(mesh, message = 'fkey')
        artist.clear_layer()
        artist.redraw()
        
        artist.draw_vertexlabels(text = {key: str(key) for key in mesh.face_vertices(fkey)})
        artist.redraw()
        pole = rhino.mesh_select_vertex(mesh, message = 'pole')
        artist.clear_layer()
        artist.redraw()
        
        rs.DeleteLayer('mesh_artist')
        
        vertex_pole(mesh, fkey, pole)
    
    if rule == 'face_opening':
        artist = rhino.MeshArtist(mesh, layer='mesh_artist')
        artist.clear_layer()
        
        artist.draw_facelabels()
        artist.redraw()
        fkey = rhino.mesh_select_face(mesh, message = 'fkey')
        artist.clear_layer()
        artist.redraw()
        
        rs.DeleteLayer('mesh_artist')
        
        face_opening(mesh, fkey)
    
    if rule == 'flat_corner_2':
        artist = rhino.MeshArtist(mesh, layer='mesh_artist')
        artist.clear_layer()
        
        artist.draw_facelabels()
        artist.redraw()
        fkey = rhino.mesh_select_face(mesh, message = 'fkey')
        artist.clear_layer()
        artist.redraw()
        
        artist.draw_vertexlabels(text = {key: str(key) for key in mesh.face_vertices(fkey)})
        artist.redraw()
        corner = rhino.mesh_select_vertex(mesh, message = 'corner')
        artist.clear_layer()
        artist.redraw()
        
        rs.DeleteLayer('mesh_artist')
        
        flat_corner_2(mesh, fkey, corner)
    
    if rule == 'flat_corner_3':
        artist = rhino.MeshArtist(mesh, layer='mesh_artist')
        artist.clear_layer()
        
        artist.draw_facelabels()
        artist.redraw()
        fkey = rhino.mesh_select_face(mesh, message = 'fkey')
        artist.clear_layer()
        artist.redraw()
        
        artist.draw_vertexlabels(text = {key: str(key) for key in mesh.face_vertices(fkey)})
        artist.redraw()
        corner = rhino.mesh_select_vertex(mesh, message = 'corner')
        artist.clear_layer()
        artist.redraw()
        
        rs.DeleteLayer('mesh_artist')
        
        flat_corner_3(mesh, fkey, corner)
    
    if rule == 'flat_corner_33':
        artist = rhino.MeshArtist(mesh, layer='mesh_artist')
        artist.clear_layer()
        
        artist.draw_facelabels()
        artist.redraw()
        fkey = rhino.mesh_select_face(mesh, message = 'fkey')
        artist.clear_layer()
        artist.redraw()
        
        artist.draw_vertexlabels(text = {key: str(key) for key in mesh.face_vertices(fkey)})
        artist.redraw()
        corner = rhino.mesh_select_vertex(mesh, message = 'corner')
        artist.clear_layer()
        artist.redraw()
        
        rs.DeleteLayer('mesh_artist')
        
        flat_corner_33(mesh, fkey, corner)
    
    if rule == 'split_35':
        artist = rhino.MeshArtist(mesh, layer='mesh_artist')
        artist.clear_layer()
        
        artist.draw_facelabels()
        artist.redraw()
        fkey = rhino.mesh_select_face(mesh, message = 'fkey')
        artist.clear_layer()
        artist.redraw()
        
        artist.draw_edgelabels(text = {(u, v): "{}-{}".format(u, v) for u, v in mesh.face_halfedges(fkey)})
        artist.redraw()
        edge = rhino.mesh_select_edge(mesh, message = 'edge')
        artist.clear_layer()
        artist.redraw()
        
        rs.DeleteLayer('mesh_artist')
        
        split_35(mesh, fkey, edge)
    
    if rule == 'split_26':
        artist = rhino.MeshArtist(mesh, layer='mesh_artist')
        artist.clear_layer()
        
        artist.draw_facelabels()
        artist.redraw()
        fkey = rhino.mesh_select_face(mesh, message = 'fkey')
        artist.clear_layer()
        artist.redraw()
        
        artist.draw_edgelabels(text = {(u, v): "{}-{}".format(u, v) for u, v in mesh.face_halfedges(fkey)})
        artist.redraw()
        edge = rhino.mesh_select_edge(mesh, message = 'edge')
        artist.clear_layer()
        artist.redraw()
        
        rs.DeleteLayer('mesh_artist')
        
        split_26(mesh, fkey, edge)
    
    if rule == 'simple_split':
        artist = rhino.MeshArtist(mesh, layer='mesh_artist')
        artist.clear_layer()
        
        artist.draw_facelabels()
        artist.redraw()
        fkey = rhino.mesh_select_face(mesh, message = 'fkey')
        artist.clear_layer()
        artist.redraw()
        
        artist.draw_edgelabels(text = {(u, v): "{}-{}".format(u, v) for u, v in mesh.face_halfedges(fkey)})
        artist.redraw()
        edge = rhino.mesh_select_edge(mesh, message = 'edge')
        artist.clear_layer()
        artist.redraw()
        
        rs.DeleteLayer('mesh_artist')
        
        simple_split(mesh, fkey, edge)
    
    if rule == 'double_split':
        artist = rhino.MeshArtist(mesh, layer='mesh_artist')
        artist.clear_layer()
        
        artist.draw_facelabels()
        artist.redraw()
        fkey = rhino.mesh_select_face(mesh, message = 'fkey')
        artist.clear_layer()
        artist.redraw()
        
        rs.DeleteLayer('mesh_artist')
        
        double_split(mesh, fkey)
    
    if rule == 'insert_pole':
        artist = rhino.MeshArtist(mesh, layer='mesh_artist')
        artist.clear_layer()
        
        artist.draw_facelabels()
        artist.redraw()
        fkey = rhino.mesh_select_face(mesh, message = 'fkey')
        artist.clear_layer()
        artist.redraw()
        
        artist.draw_vertexlabels(text = {key: str(key) for key in mesh.face_vertices(fkey)})
        artist.redraw()
        pole = rhino.mesh_select_vertex(mesh, message = 'pole')
        artist.clear_layer()
        artist.redraw()
        
        rs.DeleteLayer('mesh_artist')
        
        insert_pole(mesh, fkey, pole)
    
    if rule == 'insert_partial_pole':
        artist = rhino.MeshArtist(mesh, layer='mesh_artist')
        artist.clear_layer()
        
        artist.draw_facelabels()
        artist.redraw()
        fkey = rhino.mesh_select_face(mesh, message = 'fkey')
        artist.clear_layer()
        artist.redraw()
        
        artist.draw_vertexlabels(text = {key: str(key) for key in mesh.face_vertices(fkey)})
        artist.redraw()
        pole = rhino.mesh_select_vertex(mesh, message = 'pole')
        artist.clear_layer()
        artist.redraw()
        
        artist.draw_edgelabels({(u, v): "{}-{}".format(u, v) for u, v in mesh.face_halfedges(fkey) if u != pole and v!= pole})
        artist.redraw()
        edge = rhino.mesh_select_edge(mesh, message = 'edge')
        artist.clear_layer()
        artist.redraw()
        
        rs.DeleteLayer('mesh_artist')
        
        insert_partial_pole(mesh, fkey, pole, edge)
    
    if rule == 'face_strip_collapse':
        edge_groups, max_group = dual_edge_polylines(mesh)
        
        groups = {}
        
        for edge, group in edge_groups.items():
            u, v = edge
            if group in groups:
                if (v, u) not in groups[group]:
                    groups[group].append((u, v))
            else:
                groups[group] = [(u, v)]
        
        rs.EnableRedraw(False)
        dots = {}
        for group, edges in groups.items():
            k = float(group) / float(max_group) * 255
            RGB = [k] * 3
            rs.AddGroup(group)
            for u, v in edges:
                dot = rs.AddTextDot(group, mesh.edge_midpoint(u, v))
                dots[dot] = (u, v)
                rs.ObjectColor(dot, RGB)
                rs.AddObjectToGroup(dot, group)
        rs.EnableRedraw(True)
        
        dot = rs.GetObject('dual polyedge to collapse', filter = 8192)
        u, v = dots[dot]
        rs.DeleteObjects(dots)

        face_strip_collapse(Mesh, mesh, u, v)

    if rule == 'face_strip_insert':
        artist = rhino.MeshArtist(mesh, layer='mesh_artist')
        artist.clear_layer()

        vertex_path = []

        artist.draw_vertexlabels(text = {key: str(key) for key in mesh.vertices()})
        artist.redraw()
        vertex_path.append(rhino.mesh_select_vertex(mesh, message = 'vertex'))
        artist.clear_layer()
        artist.redraw()

        count = mesh.number_of_vertices()
        while count > 0:
            artist.draw_vertexlabels(text = {key: str(key) for key in mesh.vertex_neighbours(vertex_path[-1])})
            artist.redraw()
            vkey = rhino.mesh_select_vertex(mesh, message = 'vertex')
            artist.clear_layer()
            artist.redraw()
            if vkey in list(mesh.vertices()):
                vertex_path.append(vkey)
            else:
                break
        
        rs.DeleteLayer('mesh_artist')

        face_strip_insert(Mesh, mesh, vertex_path)
    
    return 0

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas