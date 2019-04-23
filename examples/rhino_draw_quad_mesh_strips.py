import rhinoscriptsyntax as rs
from compas_rhino.geometry import RhinoMesh
from compas_pattern.datastructures.mesh_quad.mesh_quad import QuadMesh

guids = rs.GetObjects('get quad meshes', filter = 32)
rs.EnableRedraw(False)
for guid in guids:
    mesh = QuadMesh.from_vertices_and_faces(*RhinoMesh.from_guid(guid).get_vertices_and_faces())
    mesh.collect_strips()
    polylines = [rs.AddPolyline(mesh.strip_edge_polyline(skey)) for skey in mesh.strips()]
    for polyline in polylines:
        rs.CurveArrows(polyline, 3)