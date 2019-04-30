import rhinoscriptsyntax as rs
from compas_pattern.algorithms.decomposition.algorithm import surface_decomposition

srf_guid = rs.GetObject('get surface', filter=8)
discretisation = rs.GetReal('discretisation value', 1, 0)
skeleton = surface_decomposition(srf_guid, discretisation, output_delaunay=False, output_skeleton=True, output_mesh=False, output_polysurface=False)
rs.EnableRedraw(False)
for branch in skeleton:
    rs.AddPolyline(branch)