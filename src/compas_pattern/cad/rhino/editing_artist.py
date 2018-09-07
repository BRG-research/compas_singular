try:
    import rhinoscriptsyntax as rs

except ImportError:
    import platform
    if platform.python_implementation() == 'IronPython':
        raise

import compas_rhino as rhino
import compas_rhino.artists as rhino_artist
import compas_rhino.helpers as rhino_helper

from compas.datastructures.mesh import Mesh

from compas_pattern.datastructures.pseudo_quad_mesh import PseudoQuadMesh
from compas_pattern.topology.polyline_extraction import mesh_boundaries

from compas_pattern.topology.grammar import face_pole
from compas_pattern.topology.grammar import edge_pole
from compas_pattern.topology.grammar import vertex_pole
from compas_pattern.topology.grammar import add_opening
from compas_pattern.topology.grammar import close_opening
from compas_pattern.topology.grammar import flat_corner_2
from compas_pattern.topology.grammar import flat_corner_3
from compas_pattern.topology.grammar import flat_corner_33
from compas_pattern.topology.grammar import split_35
from compas_pattern.topology.grammar import split_35_diag
from compas_pattern.topology.grammar import split_26
from compas_pattern.topology.grammar import simple_split
from compas_pattern.topology.grammar import double_split
from compas_pattern.topology.grammar import insert_pole
from compas_pattern.topology.grammar import insert_partial_pole
from compas_pattern.topology.grammar import singular_boundary_1
from compas_pattern.topology.grammar import singular_boundary_2
from compas_pattern.topology.grammar import singular_boundary_minus_1
from compas_pattern.topology.grammar import add_handle
from compas_pattern.topology.grammar import close_handle
from compas_pattern.topology.grammar import close_handle_2

from compas_pattern.topology.polyline_extraction import dual_edge_polylines

from compas_pattern.topology.face_strip_operations import face_strip_collapse
from compas_pattern.topology.face_strip_operations import face_strip_insert

from compas_pattern.topology.grammar import rotate_vertex

from compas_pattern.topology.grammar import clear_faces

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2017, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'


__all__ = [
    'apply_rule',
]


def apply_rule(mesh, rule):

    if rule == 'face_pole':
        artist = rhino_artist.MeshArtist(mesh, layer='mesh_artist')
        artist.clear_layer()
        
        artist.draw_facelabels()
        artist.redraw()
        fkey = rhino_helper.mesh_select_face(mesh, message = 'fkey')
        artist.clear_layer()
        artist.redraw()
        
        rs.DeleteLayer('mesh_artist')
        
        face_pole(mesh, fkey)
    
    elif rule == 'edge_pole':
        artist = rhino_artist.MeshArtist(mesh, layer='mesh_artist')
        artist.clear_layer()
        
        artist.draw_facelabels()
        artist.redraw()
        fkey = rhino_helper.mesh_select_face(mesh, message = 'fkey')
        artist.clear_layer()
        artist.redraw()
        
        artist.draw_edgelabels(text = {(u, v): "{}-{}".format(u, v) for u, v in mesh.face_halfedges(fkey)})
        artist.redraw()
        edge = rhino_helper.mesh_select_edge(mesh, message = 'edge')
        artist.clear_layer()
        artist.redraw()
        
        rs.DeleteLayer('mesh_artist')
        
        edge_pole(mesh, fkey, edge)
    
    elif rule == 'vertex_pole':
        artist = rhino_artist.MeshArtist(mesh, layer='mesh_artist')
        artist.clear_layer()
        
        artist.draw_facelabels()
        artist.redraw()
        fkey = rhino_helper.mesh_select_face(mesh, message = 'fkey')
        artist.clear_layer()
        artist.redraw()
        
        artist.draw_vertexlabels(text = {key: str(key) for key in mesh.face_vertices(fkey)})
        artist.redraw()
        pole = rhino_helper.mesh_select_vertex(mesh, message = 'pole')
        artist.clear_layer()
        artist.redraw()
        
        rs.DeleteLayer('mesh_artist')
        
        vertex_pole(mesh, fkey, pole)
    
    elif rule == 'add_opening':
        artist = rhino_artist.MeshArtist(mesh, layer='mesh_artist')
        artist.clear_layer()
        
        artist.draw_facelabels()
        artist.redraw()
        fkey = rhino_helper.mesh_select_face(mesh, message = 'fkey')
        artist.clear_layer()
        artist.redraw()
        
        rs.DeleteLayer('mesh_artist')
        
        face_opening(mesh, fkey)

    elif rule == 'close_opening':
        artist = rhino_artist.MeshArtist(mesh, layer='mesh_artist')
        artist.clear_layer()
        
        boundaries = mesh_boundaries(mesh)
        artist.draw_vertexlabels(text = {key: str(key) for key in [vkey for boundary in boundaries for vkey in boundary]})
        artist.redraw()
        vkey = rhino_helper.mesh_select_vertex(mesh, message = 'vertex on the opening to close')
        artist.clear_layer()
        artist.redraw()

        rs.DeleteLayer('mesh_artist')
        
        for boundary in boundaries:
            if vkey in boundary:
                vkeys = boundary
                break

        close_opening(mesh, vkeys)
    
    elif rule == 'flat_corner_2':
        artist = rhino_artist.MeshArtist(mesh, layer='mesh_artist')
        artist.clear_layer()
        
        artist.draw_facelabels()
        artist.redraw()
        fkey = rhino_helper.mesh_select_face(mesh, message = 'fkey')
        artist.clear_layer()
        artist.redraw()
        
        artist.draw_vertexlabels(text = {key: str(key) for key in mesh.face_vertices(fkey)})
        artist.redraw()
        corner = rhino_helper.mesh_select_vertex(mesh, message = 'corner')
        artist.clear_layer()
        artist.redraw()
        
        rs.DeleteLayer('mesh_artist')
        
        flat_corner_2(mesh, fkey, corner)
    
    elif rule == 'flat_corner_3':
        artist = rhino_artist.MeshArtist(mesh, layer='mesh_artist')
        artist.clear_layer()
        
        artist.draw_facelabels()
        artist.redraw()
        fkey = rhino_helper.mesh_select_face(mesh, message = 'fkey')
        artist.clear_layer()
        artist.redraw()
        
        artist.draw_vertexlabels(text = {key: str(key) for key in mesh.face_vertices(fkey)})
        artist.redraw()
        corner = rhino_helper.mesh_select_vertex(mesh, message = 'corner')
        artist.clear_layer()
        artist.redraw()
        
        rs.DeleteLayer('mesh_artist')
        
        flat_corner_3(mesh, fkey, corner)
    
    elif rule == 'flat_corner_33':
        artist = rhino_artist.MeshArtist(mesh, layer='mesh_artist')
        artist.clear_layer()
        
        artist.draw_facelabels()
        artist.redraw()
        fkey = rhino_helper.mesh_select_face(mesh, message = 'fkey')
        artist.clear_layer()
        artist.redraw()
        
        artist.draw_vertexlabels(text = {key: str(key) for key in mesh.face_vertices(fkey)})
        artist.redraw()
        corner = rhino_helper.mesh_select_vertex(mesh, message = 'corner')
        artist.clear_layer()
        artist.redraw()
        
        rs.DeleteLayer('mesh_artist')
        
        flat_corner_33(mesh, fkey, corner)
    
    elif rule == 'split_35':
        artist = rhino_artist.MeshArtist(mesh, layer='mesh_artist')
        artist.clear_layer()
        
        artist.draw_facelabels()
        artist.redraw()
        fkey = rhino_helper.mesh_select_face(mesh, message = 'fkey')
        artist.clear_layer()
        artist.redraw()
        
        artist.draw_edgelabels(text = {(u, v): "{}-{}".format(u, v) for u, v in mesh.face_halfedges(fkey)})
        artist.redraw()
        edge = rhino_helper.mesh_select_edge(mesh, message = 'edge')
        artist.clear_layer()
        artist.redraw()
        
        rs.DeleteLayer('mesh_artist')
        
        split_35(mesh, fkey, edge)

    elif rule == 'split_35_diag':
        artist = rhino_artist.MeshArtist(mesh, layer='mesh_artist')
        artist.clear_layer()
        
        artist.draw_facelabels()
        artist.redraw()
        fkey = rhino_helper.mesh_select_face(mesh, message = 'fkey')
        artist.clear_layer()
        artist.redraw()
        
        artist.draw_vertexlabels(text = {key: str(key) for key in mesh.face_vertices(fkey)})
        artist.redraw()
        corner = rhino_helper.mesh_select_vertex(mesh, message = 'corner')
        artist.clear_layer()
        artist.redraw()
        
        rs.DeleteLayer('mesh_artist')
        
        split_35_diag(mesh, fkey, corner)
    
    elif rule == 'split_26':
        artist = rhino_artist.MeshArtist(mesh, layer='mesh_artist')
        artist.clear_layer()
        
        artist.draw_facelabels()
        artist.redraw()
        fkey = rhino_helper.mesh_select_face(mesh, message = 'fkey')
        artist.clear_layer()
        artist.redraw()

        artist.draw_edgelabels(text = {(u, v): "{}-{}".format(u, v) for u, v in mesh.face_halfedges(fkey)})
        artist.redraw()
        edge = rhino_helper.mesh_select_edge(mesh, message = 'edge')
        artist.clear_layer()
        artist.redraw()
        
        rs.DeleteLayer('mesh_artist')
        
        split_26(mesh, fkey, edge)
    
    elif rule == 'simple_split':
        artist = rhino_artist.MeshArtist(mesh, layer='mesh_artist')
        artist.clear_layer()
        
        artist.draw_facelabels()
        artist.redraw()
        fkey = rhino_helper.mesh_select_face(mesh, message = 'fkey')
        artist.clear_layer()
        artist.redraw()
        
        artist.draw_edgelabels(text = {(u, v): "{}-{}".format(u, v) for u, v in mesh.face_halfedges(fkey)})
        artist.redraw()
        edge = rhino_helper.mesh_select_edge(mesh, message = 'edge')
        artist.clear_layer()
        artist.redraw()
        
        rs.DeleteLayer('mesh_artist')
        
        simple_split(mesh, fkey, edge)
    
    elif rule == 'double_split':
        artist = rhino_artist.MeshArtist(mesh, layer='mesh_artist')
        artist.clear_layer()
        
        artist.draw_facelabels()
        artist.redraw()
        fkey = rhino_helper.mesh_select_face(mesh, message = 'fkey')
        artist.clear_layer()
        artist.redraw()
        
        rs.DeleteLayer('mesh_artist')
        
        double_split(mesh, fkey)
    
    elif rule == 'insert_pole':
        artist = rhino_artist.MeshArtist(mesh, layer='mesh_artist')
        artist.clear_layer()
        
        artist.draw_facelabels()
        artist.redraw()
        fkey = rhino_helper.mesh_select_face(mesh, message = 'fkey')
        artist.clear_layer()
        artist.redraw()
        
        artist.draw_vertexlabels(text = {key: str(key) for key in mesh.face_vertices(fkey)})
        artist.redraw()
        pole = rhino_helper.mesh_select_vertex(mesh, message = 'pole')
        artist.clear_layer()
        artist.redraw()
        
        rs.DeleteLayer('mesh_artist')
        
        insert_pole(mesh, fkey, pole)
    
    elif rule == 'insert_partial_pole':
        artist = rhino_artist.MeshArtist(mesh, layer='mesh_artist')
        artist.clear_layer()
        
        artist.draw_facelabels()
        artist.redraw()
        fkey = rhino_helper.mesh_select_face(mesh, message = 'fkey')
        artist.clear_layer()
        artist.redraw()
        
        artist.draw_vertexlabels(text = {key: str(key) for key in mesh.face_vertices(fkey)})
        artist.redraw()
        pole = rhino_helper.mesh_select_vertex(mesh, message = 'pole')
        artist.clear_layer()
        artist.redraw()
        
        artist.draw_edgelabels({(u, v): "{}-{}".format(u, v) for u, v in mesh.face_halfedges(fkey) if u != pole and v!= pole})
        artist.redraw()
        edge = rhino_helper.mesh_select_edge(mesh, message = 'edge')
        artist.clear_layer()
        artist.redraw()
        
        rs.DeleteLayer('mesh_artist')
        
        insert_partial_pole(mesh, fkey, pole, edge)
    
    elif rule == 'singular_boundary_1':
        artist = rhino_artist.MeshArtist(mesh, layer='mesh_artist')
        artist.clear_layer()
        
        artist.draw_edgelabels(text = {(u, v): "{}-{}".format(u, v) for u, v in mesh.edges()})
        artist.redraw()
        edge = rhino_helper.mesh_select_edge(mesh, message = 'edge')
        artist.clear_layer()
        artist.redraw()

        artist.draw_vertexlabels(text = {key: str(key) for key in edge})
        artist.redraw()
        vkey = rhino_helper.mesh_select_vertex(mesh, message = 'vkey')
        artist.clear_layer()
        artist.redraw()
        
        rs.DeleteLayer('mesh_artist')
        
        singular_boundary_1(mesh, edge, vkey)

    elif rule == 'singular_boundary_2':
        artist = rhino_artist.MeshArtist(mesh, layer='mesh_artist')
        artist.clear_layer()
        
        artist.draw_edgelabels(text = {(u, v): "{}-{}".format(u, v) for u, v in mesh.edges()})
        artist.redraw()
        edge = rhino_helper.mesh_select_edge(mesh, message = 'edge')
        artist.clear_layer()
        artist.redraw()

        artist.draw_vertexlabels(text = {key: str(key) for key in edge})
        artist.redraw()
        vkey = rhino_helper.mesh_select_vertex(mesh, message = 'vkey')
        artist.clear_layer()
        artist.redraw()
        
        rs.DeleteLayer('mesh_artist')
        
        singular_boundary_2(mesh, edge, vkey)
        
    elif rule == 'singular_boundary_minus_1':
        artist = rhino_artist.MeshArtist(mesh, layer='mesh_artist')
        artist.clear_layer()
        
        artist.draw_facelabels()
        artist.redraw()
        fkey = rhino_helper.mesh_select_face(mesh, message = 'fkey')
        artist.clear_layer()
        artist.redraw()

        artist.draw_vertexlabels(text = {key: str(key) for key in mesh.face_vertices(fkey)})
        artist.redraw()
        vkey = rhino_helper.mesh_select_vertex(mesh, message = 'vkey')
        artist.clear_layer()
        artist.redraw()
        
        rs.DeleteLayer('mesh_artist')
        
        singular_boundary_minus_1(mesh, fkey, vkey)

    elif rule == 'face_strip_collapse':
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

        face_strip_collapse(PseudoQuadMesh, mesh, u, v)

    elif rule == 'face_strip_insert':
        artist = rhino_artist.MeshArtist(mesh, layer='mesh_artist')
        artist.clear_layer()

        vertex_path = []
        count = mesh.number_of_vertices() * 1.5
        artist.draw_vertexlabels(text = {key: str(key) for key in mesh.vertices()})
        artist.redraw()
        while count > 0:
            count -= 1    
            vkey = rhino_helper.mesh_select_vertex(mesh, message = 'vertex')
            if vkey is None:
                artist.clear_layer()
                artist.redraw()
                break
            else:
                vertex_path.append(vkey)

        rs.DeleteLayer('mesh_artist')

        start_pole = rs.GetInteger(message='pole at the start?', number=0, minimum=0, maximum=1)
        end_pole = rs.GetInteger(message='pole at the end?', number=0, minimum=0, maximum=1)

        mesh = face_strip_insert(PseudoQuadMesh, mesh, vertex_path, pole_extremities = [start_pole, end_pole])

    elif rule == 'rotate_vertex':
        artist = rhino_artist.MeshArtist(mesh, layer='mesh_artist')
        artist.clear_layer()

        artist.draw_vertexlabels(text = {key: str(key) for key in mesh.vertices()})
        artist.redraw()
        vkey = rhino_helper.mesh_select_vertex(mesh, message = 'vkey')
        artist.clear_layer()
        artist.redraw()

        rs.DeleteLayer('mesh_artist')
        
        rotate_vertex(mesh, vkey)

    elif rule == 'clear_faces':
        artist = rhino_artist.MeshArtist(mesh, layer='mesh_artist')
        artist.clear_layer()

        artist.draw_facelabels()
        artist.redraw()
        fkeys = rhino_helper.mesh_select_faces(mesh, message = 'fkeys')
        artist.clear_layer()
        artist.redraw()

        vertices = [mesh.vertex_coordinates(vkey) for vkey in mesh.vertices()]
        face_vertices = [mesh.face_vertices(fkey) for fkey in fkeys]

        faces_mesh = PseudoQuadMesh.from_vertices_and_faces(vertices, face_vertices)
        faces_boundary_vertices = mesh_boundaries(faces_mesh)[0]

        artist.draw_vertexlabels(text = {key: str(key) for key in faces_boundary_vertices})
        artist.redraw()
        vkeys = rhino_helper.mesh_select_vertices(mesh, message = 'vkeys')
        artist.clear_layer()
        artist.redraw()

        rs.DeleteLayer('mesh_artist')
        
        clear_faces(mesh, fkeys, vkeys)

    elif rule == 'add_handle':
        artist = rhino_artist.MeshArtist(mesh, layer='mesh_artist')
        artist.clear_layer()
        
        artist.draw_facelabels()
        artist.redraw()
        fkey_1 = rhino_helper.mesh_select_face(mesh, message = 'fkey_1')
        artist.clear_layer()
        artist.redraw()

        artist.draw_facelabels()
        artist.redraw()
        fkey_2 = rhino_helper.mesh_select_face(mesh, message = 'fkey_2')
        artist.clear_layer()
        artist.redraw()
        
        rs.DeleteLayer('mesh_artist')
        
        add_handle(mesh, fkey_1, fkey_2)

    elif rule == 'close_handle':
        artist = rhino_artist.MeshArtist(mesh, layer='mesh_artist')
        artist.clear_layer()
        
        artist.draw_facelabels()
        artist.redraw()
        fkey_1 = rhino_helper.mesh_select_face(mesh, message = 'fkey_1')
        artist.clear_layer()
        artist.redraw()

        artist.draw_facelabels(text = {key: str(key) for key in mesh.face_neighbors(fkey_1)})
        artist.redraw()
        fkey_2 = rhino_helper.mesh_select_face(mesh, message = 'fkey_2')
        artist.clear_layer()
        artist.redraw()
        
        rs.DeleteLayer('mesh_artist')


        count = mesh.number_of_faces()
        fkeys = [fkey_1, fkey_2]
        while count > 0:
            count -= 1
            u, v = mesh.face_adjacency_halfedge(fkeys[-2], fkeys[-1])
            w = mesh.face_vertex_ancestor(fkeys[-1], v)
            x = mesh.face_vertex_ancestor(fkeys[-1], w)
            if x in mesh.halfedge[w] and mesh.halfedge[w][x] is not None:
                fkey_3 = mesh.halfedge[w][x]
                fkeys.append(fkey_3)
                if fkeys[-1] == fkeys[0]:
                    break

        close_handle(mesh, fkeys)

    elif rule == 'close_handle_2':
        artist = rhino_artist.MeshArtist(mesh, layer='mesh_artist')
        artist.clear_layer()

        edge_paths = []
        for i in range(2):

            vertex_path = []

            artist.draw_vertexlabels(text = {key: str(key) for key in mesh.vertices()})
            artist.redraw()
            vertex_path.append(rhino_helper.mesh_select_vertex(mesh, message = 'vertex'))
            artist.clear_layer()
            artist.redraw()

            count = mesh.number_of_vertices()
            while count > 0:
                count -= 1
                artist.draw_vertexlabels(text = {key: str(key) for key in mesh.vertex_neighbors(vertex_path[-1])})
                artist.redraw()
                vkey = rhino_helper.mesh_select_vertex(mesh, message = 'vertex')
                if vkey is None:
                    break
                artist.clear_layer()
                artist.redraw()
                if vkey in list(mesh.vertices()):
                    vertex_path.append(vkey)
                else:
                    break
                if vkey  == vertex_path[0]:
                    break
            del vertex_path[-1]
            edge_paths.append([[vertex_path[i - 1], vertex_path[i]] for i in range(len(vertex_path))])

        rs.DeleteLayer('mesh_artist')

        edge_path_1, edge_path_2 = edge_paths

        mesh = close_handle_2(mesh, edge_path_1, edge_path_2)

    elif rule == 'move_vertices':
        artist = rhino_artist.MeshArtist(mesh, layer='mesh_artist')
        artist.clear_layer()

        artist.draw_vertexlabels(text = {key: str(key) for key in mesh.vertices()})
        artist.redraw()
        vkeys = rhino_helper.mesh_select_vertices(mesh, message = 'vkeys')
        artist.clear_layer()
        artist.redraw()

        rs.DeleteLayer('mesh_artist')
        
        x1, y1, z1 = rs.GetPoint(message = 'from...')
        x2, y2, z2 = rs.GetPoint(message = '...to')

        for vkey in vkeys:
            attr = mesh.vertex[vkey]
            attr['x'] += x2 - x1
            attr['y'] += y2 - y1
            attr['z'] += z2 - z1

    elif rule == 'project_on_surface':
        srf = rs.GetObject('surface for projection', filter = 8)
        for vkey in mesh.vertices():
            u, v = rs.SurfaceClosestPoint(srf, mesh.vertex_coordinates(vkey))
            x, y, z = rs.EvaluateSurface(srf, u, v)
            attr = mesh.vertex[vkey]
            attr['x'] = x
            attr['y'] = y
            attr['z'] = z

    return 0

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas