import rhinoscriptsyntax as rs

from compas_pattern.cad.rhino.objects.surface import RhinoSurface

from compas_pattern.algorithms.skeletonisation import surface_skeleton
from compas_pattern.algorithms.skeletonisation import surface_skeleton_decomposition_mesh
from compas_pattern.algorithms.skeletonisation import surface_skeleton_decomposition_nurbs

from compas_pattern.algorithms.smoothing import surface_constrained_smoothing

from compas_pattern.cad.rhino.utilities import draw_mesh

precision = 1
density = 3

srf = RhinoSurface.from_selection()

rs.EnableRedraw(False)

#srfs = surface_skeleton_decomposition_nurbs(srf.guid, precision)

mesh = surface_skeleton_decomposition_mesh(srf.guid, precision)
draw_mesh(mesh)
#mesh.init_strip_density()
#mesh.set_strips_density_target(density)
#mesh.densification()
#surface_constrained_smoothing(mesh.quad_mesh, srf, algorithm = 'area')
#quad_mesh_guid = draw_mesh(mesh.quad_mesh)

rs.EnableRedraw(True)
