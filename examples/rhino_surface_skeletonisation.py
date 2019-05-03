import rhinoscriptsyntax as rs
from compas_pattern.algorithms.decomposition.algorithm import surface_decomposition

srf_guid = rs.GetObject('get surface', filter=8)
crv_guids = rs.GetObjects('get curves', filter=4) or []
pt_guids = rs.GetObjects('get points', filter=1) or []
discretisation = rs.GetReal('discretisation value', 1, 0)
polylines = surface_decomposition(srf_guid, discretisation, crv_guids = crv_guids, pt_guids = pt_guids, output_delaunay=False, output_skeleton=False, output_decomposition=True, output_mesh=False, output_polysurface=False)[0]
rs.EnableRedraw(False)
for branch in polylines:
    rs.AddPolyline(branch)