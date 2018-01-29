import rhinoscriptsyntax as rs

from compas.datastructures.mesh import Mesh
import compas_rhino as rhino

from compas_pattern.topology.joining_welding import join_and_weld_meshes

from compas.geometry.algorithms.smoothing import mesh_smooth_area

quad_mesh = rs.GetObject('quad_mesh', filter = 32)
quad_mesh = rhino.mesh_from_guid(Mesh, quad_mesh)

t = rs.GetReal('parameter', number = .25, minimum = 0, maximum = 1)

if not quad_mesh.is_quadmesh():
    print 'not quad mesh'

face_meshes = []
for fkey in quad_mesh.faces():
    e = quad_mesh.face_centroid(fkey)
    halfedges = quad_mesh.face_halfedges(fkey)
    for i, edge in enumerate(halfedges):
        u, v = edge
        a = quad_mesh.edge_point(u, v, t)
        b = quad_mesh.edge_point(u, v, 1 - t)
        c = quad_mesh.vertex_coordinates(v)
        u, v = halfedges[i + 1 - len(halfedges)]
        d = quad_mesh.edge_point(u, v, t)
        vertices = [a, b, c, d, e]
        face_vertices = [[0, 1, 2, 3, 4]]
        face_mesh = Mesh.from_vertices_and_faces(vertices, face_vertices)
        face_meshes.append(face_mesh)

penta_mesh = join_and_weld_meshes(Mesh, face_meshes)

fixed_vertices = penta_mesh.vertices_on_boundary()

mesh_smooth_area(penta_mesh, fixed = fixed_vertices, kmax = 20, damping = .5)


rs.EnableRedraw(False)
for u, v in penta_mesh.edges():
    u_xyz = penta_mesh.vertex_coordinates(u)
    v_xyz = penta_mesh.vertex_coordinates(v)
    if u_xyz != v_xyz:
        rs.AddLine(u_xyz, v_xyz)
rs.EnableRedraw(True)

#vertices = [penta_mesh.vertex_coordinates(vkey) for vkey in penta_mesh.vertices()]
#face_vertices = [penta_mesh.face_vertices(fkey) for fkey in penta_mesh.faces()]
#penta_mesh_guid = rhino.utilities.drawing.xdraw_mesh(vertices, face_vertices, None, None)
