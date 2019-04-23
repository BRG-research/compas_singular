import rhinoscriptsyntax as rs
from compas_rhino.geometry import RhinoMesh
from compas_pattern.datastructures.mesh_quad.mesh_quad import QuadMesh

guids = rs.GetObjects('get quad meshes', filter = 32)
rs.EnableRedraw(False)
for guid in guids:
    mesh = QuadMesh.from_vertices_and_faces(*RhinoMesh.from_guid(guid).get_vertices_and_faces())
    polylines = [rs.AddPolyline(polyline) for polyline in mesh.polylines()]