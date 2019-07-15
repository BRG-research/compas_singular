import rhinoscriptsyntax as rs
from compas_rhino.geometry import RhinoMesh
from compas_pattern.datastructures.mesh_quad_pseudo_coarse.mesh_quad_pseudo_coarse import CoarsePseudoQuadMesh
from compas_pattern.cad.rhino.artist import select_quad_mesh_strip
from compas_rhino.artists import MeshArtist

guid = rs.GetObject('get (coarse) quad mesh', filter = 32)
poles = rs.GetObjects('get pole points', filter = 1)
if poles is None:
    poles = []
else:
    poles = [rs.PointCoordinates(pole) for pole in poles]

vertices, faces = RhinoMesh.from_guid(guid).get_vertices_and_faces()
mesh = CoarsePseudoQuadMesh.from_vertices_and_faces_with_poles(vertices, faces, poles)
mesh.collect_strips()
mesh.set_strips_density(1)
mesh.densification()


count = 100
while count:
    count -= 1
    
    artist = MeshArtist(mesh.get_quad_mesh())
    guid = artist.draw_mesh()
    
    operation = rs.GetString('operation?', strings=['global_density_value', 'global_subdivision_target_length', 'strip_density_value', 'strip_subdivision_target_length', 'global_uniform_target_number_faces', 'exit'])
    
    # stop if asked
    if operation is None or operation == 'exit':
        break

    # get operation parameters
    if 'strip' in operation:
        skey = select_quad_mesh_strip(mesh, show_density=True)
    if 'value' in operation:
        d = rs.GetInteger('density value', number=3, minimum=1)
    elif 'length' in operation:
        t = rs.GetReal('density target', number=1.)
    elif 'faces' in operation:
        nb_faces = rs.GetInteger('density value', number=100, minimum=1)

    # apply operation
    if operation == 'strip_density_value':
        mesh.set_strip_density(skey, d)

    elif operation == 'global_density_value':
        mesh.set_strips_density(d)

    elif operation == 'strip_subdivision_target_length':
        mesh.set_strip_density_target(skey, t)

    elif operation == 'global_subdivision_target_length':
        mesh.set_strips_density_target(t)

    elif operation == 'global_uniform_target_number_faces':
        mesh.set_mesh_density_face_target(nb_faces)

    # update data
    mesh.densification()

    # delete drawing
    rs.DeleteObjects(guid)

