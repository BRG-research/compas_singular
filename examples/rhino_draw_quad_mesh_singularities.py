import rhinoscriptsyntax as rs
from compas_rhino.geometry import RhinoMesh
from compas_pattern.datastructures.mesh_quad_pseudo.mesh_quad_pseudo import PseudoQuadMesh

guids = rs.GetObjects('get (pseudo-)quad meshes', filter = 32)
poles = [rs.PointCoordinates(point) for point in rs.GetObjects('get poles', filter = 1) or []]
radius = rs.GetReal('circle radius', number = 1)
rs.EnableRedraw(False)
for guid in guids:
    vertices, faces = RhinoMesh.from_guid(guid).get_vertices_and_faces()
    mesh = PseudoQuadMesh.from_vertices_and_faces_with_poles(vertices, faces, poles)
    circles = [rs.AddCircle(mesh.vertex_coordinates(vkey), radius) for vkey in mesh.singularities()]
