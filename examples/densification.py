import rhinoscriptsyntax as rs

from compas.datastructures.mesh import Mesh
import compas_rhino as rhino

from compas.utilities import geometric_key

from compas_pattern.datastructures.pseudo_quad_mesh import PseudoQuadMesh
from compas_pattern.algorithms.coarse_to_dense_mesh import quad_mesh_densification

conform_mesh = rs.GetObject('mesh to densify', filter = 32)
conform_mesh = rhino.mesh_from_guid(PseudoQuadMesh, conform_mesh)

poles = rs.GetObjects('pole points', filter = 1)
if poles is None:
    poles = []
poles = [geometric_key(rs.PointCoordinates(pt)) for pt in poles]

target_length = rs.GetReal('target length for densification', number = 1)

rs.EnableRedraw(False)

# pole points

for fkey in conform_mesh.faces():
    face_vertices = conform_mesh.face_vertices(fkey)
    if len(face_vertices) == 3:
        # find pole location
        pole = None
        for vkey in face_vertices:
            geom_key = geometric_key(conform_mesh.vertex_coordinates(vkey))
            if geom_key in poles:
                pole = vkey
                break
        # modify face
        if pole is not None:
            new_face_vertices = face_vertices[:]
            idx = new_face_vertices.index(vkey)
            new_face_vertices.insert(idx, vkey)
            conform_mesh.delete_face(fkey)
            conform_mesh.add_face(new_face_vertices, fkey)
print conform_mesh
for fkey in conform_mesh.faces():
    val = len(conform_mesh.face_vertices(fkey))
    if val != 4:
        xyz = conform_mesh.face_centroid(fkey)
        rs.AddTextDot(val, xyz)
dense_mesh = quad_mesh_densification(conform_mesh, target_length)
print dense_mesh

vertices = [dense_mesh.vertex_coordinates(vkey) for vkey in dense_mesh.vertices()]
face_vertices = [dense_mesh.face_vertices(fkey) for fkey in dense_mesh.faces()]
dense_mesh_guid = rhino.utilities.drawing.xdraw_mesh(vertices, face_vertices, None, None)
#layer_name = 'dense_mesh_6'
#rs.AddLayer(layer_name)
#rs.ObjectLayer(dense_mesh_guid, layer = layer_name)

rs.EnableRedraw(True)