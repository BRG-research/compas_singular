import rhinoscriptsyntax as rs

from compas_pattern.cad.rhino.objects.surface import RhinoSurface

from compas_pattern.algorithms.skeletonisation import surface_skeleton
from compas_pattern.algorithms.skeletonisation import surface_skeleton_decomposition_mesh
from compas_pattern.algorithms.skeletonisation import surface_skeleton_decomposition_nurbs

from compas_pattern.algorithms.smoothing import surface_constrained_smoothing

from compas_pattern.cad.rhino.utilities import draw_mesh

precision = .2
density = 3

surfaces = rs.GetObjects('surfaces', filter = 8)

rs.EnableRedraw(False)

for surface in surfaces:
    srf = RhinoSurface(surface)
    
    #srfs = surface_skeleton_decomposition_nurbs(srf.guid, precision)
    
    delaunay, branches = surface_skeleton(srf.guid, precision)
    mesh = surface_skeleton_decomposition_mesh(srf.guid, precision)
    rs.ObjectLayer([rs.AddPolyline(branch) for branch in branches], 'branches')
    rs.ObjectLayer(draw_mesh(delaunay), 'delaunay')
    rs.ObjectLayer(draw_mesh(mesh), 'mesh')
    #mesh.init_strip_density()
    #mesh.set_strips_density_target(density)
    #mesh.densification()
    #surface_constrained_smoothing(mesh.quad_mesh, srf, algorithm = 'area')
    #quad_mesh_guid = draw_mesh(mesh.quad_mesh)
    
    rs.EnableRedraw(True)
