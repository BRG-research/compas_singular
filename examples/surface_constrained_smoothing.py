import rhinoscriptsyntax as rs
from compas_pattern.cad.rhino.objects.surface import RhinoSurface
from compas_rhino.geometry.mesh import RhinoMesh
from compas_pattern.datastructures.mesh import Mesh
from compas_pattern.datastructures.mesh_quad_coarse import CoarseQuadMesh
from compas_pattern.cad.rhino.smoothing_constraints import automated_smoothing_constraints
from compas_pattern.cad.rhino.smoothing_constraints import automated_smoothing_surface_constraints
from compas_pattern.algorithms.smoothing import constrained_smoothing
from compas_pattern.cad.rhino.utilities import draw_mesh

srf = RhinoSurface.from_selection()

guids = rs.GetObjects('get meshes', filter = 32)

for guid in guids:
    mesh = CoarseQuadMesh.from_vertices_and_faces(*RhinoMesh.from_guid(guid).get_vertices_and_faces())
    
    mesh.collect_strips()
    mesh.init_strip_density()
    #mesh.set_strips_density(6)
    mesh.set_strips_density_target(.5)
    mesh.densification()
    
    constraints = automated_smoothing_surface_constraints(mesh.quad_mesh, srf)
    constrained_smoothing(mesh.quad_mesh, kmax = 100, damping = .5, constraints = constraints, algorithm = 'area')
    
    new_guid = draw_mesh(mesh.quad_mesh)
    rs.MoveObject(new_guid, [11,0,0])