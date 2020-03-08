import rhinoscriptsyntax as rs
from compas_rhino.geometry import RhinoMesh
from compas_pattern.datastructures.mesh_quad_pseudo.mesh_quad_pseudo import PseudoQuadMesh
from compas_pattern.cad.rhino.draw import draw_graph

guids = rs.GetObjects('get quad meshes', filter = 32)
poles = rs.GetObjects('get pole points', filter = 1)
if poles is None:
    poles = []
else:
    poles = [rs.PointCoordinates(pole) for pole in poles]
rs.EnableRedraw(False)
for guid in guids:
    vertices, faces = RhinoMesh.from_guid(guid).get_vertices_and_faces()
    mesh = PseudoQuadMesh.from_vertices_and_faces_with_poles(vertices, faces, poles)
    #mesh = QuadMesh.from_vertices_and_faces(*RhinoMesh.from_guid(guid).get_vertices_and_faces())
    #print('euler', mesh.euler())
    #print('nb_boundaries', len(mesh.boundaries()))
    #mesh.collect_strips()
    #mesh.collect_polyedges()
    #polylines = [rs.AddPolyline(mesh.strip_edge_midpoint_polyline(skey)) for skey in mesh.strips()]
    #for i, polyline in enumerate(polylines):
    #    
    #polylines = [rs.AddPolyline(polyline) for polyline in mesh.singularity_polylines()]
    #polylines = [rs.AddPolyline(polyline) for polyline in mesh.polylines()]
    #for polyline in polylines:
    #    rs.CurveArrows(polyline, 3)
    #for i, vkey in enumerate(mesh.vertices()):
    #    rs.AddCircle(mesh.vertex_coordinates(vkey), 2)
    #    rs.AddText(str(i), mesh.vertex_coordinates(vkey), 2)
    #circles = [rs.AddCircle(mesh.vertex_coordinates(vkey), 1) for vkey in mesh.singularities()]
    circles = [rs.AddCircle(mesh.vertex_coordinates(vkey), .25) for vkey in mesh.singularities()]
    #vertices, edges = mesh.strip_graph()
    #circles = [rs.AddCircle(xyz, .125) for xyz in vertices.values()]
    #draw_graph(vertices, edges, spindle_size=5, node_radius=.125)
    #rs.AddText(mesh.number_of_strips(), mesh.centroid())
    #rs.AddCircle(mesh.centroid(), 2)