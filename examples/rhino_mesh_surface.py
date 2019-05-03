import rhinoscriptsyntax as rs
from compas_pattern.cad.rhino.objects.surface import RhinoSurface
from compas_pattern.algorithms.decomposition.algorithm import surface_decomposition
from compas_pattern.algorithms.relaxation.constraints import automated_smoothing_constraints
from compas_pattern.algorithms.relaxation.constraints import automated_smoothing_surface_constraints
from compas_pattern.algorithms.relaxation.relaxation import constrained_smoothing
from compas_pattern.cad.rhino.draw import draw_mesh

srf_guid = rs.GetObject('get surface', filter=8)
#crv_guids = rs.GetObjects('get curves', filter=4) or []
crv_guids = []
pt_guids = rs.GetObjects('get points', filter=1) or []
poles = [rs.PointCoordinates(pt) for pt in pt_guids]

settings = rs.PropertyListBox(['triangulation_precision', 'density_target', 'smoothing_iterations', 'damping_value'], [0.5, 1.0, 30, 0.5], 'settings for mesh on surface')
triangulation_precision, density_target, kmax, damping = settings

# topology
print 'decomposition...'
coarse_quad_mesh = surface_decomposition(srf_guid, float(triangulation_precision), crv_guids = crv_guids, pt_guids = pt_guids, output_delaunay=False, output_skeleton=False, output_mesh=True, output_polysurface=False)[0]

# density
print 'densification...'
coarse_quad_mesh.init_strip_density()
coarse_quad_mesh.set_strips_density_target(float(density_target))
coarse_quad_mesh.densification()

# smoothing
print 'smoothing...'
constraints = automated_smoothing_surface_constraints(coarse_quad_mesh.quad_mesh, RhinoSurface(srf_guid))
constraints.update(automated_smoothing_constraints(coarse_quad_mesh.quad_mesh, pt_guids))
constrained_smoothing(coarse_quad_mesh.quad_mesh, kmax = int(kmax), damping = float(damping), constraints = constraints, algorithm = 'area')

rs.EnableRedraw(False)
draw_mesh(coarse_quad_mesh.quad_mesh)