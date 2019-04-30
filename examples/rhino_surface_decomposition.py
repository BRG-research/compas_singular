import rhinoscriptsyntax as rs
from compas_pattern.algorithms.decomposition.algorithm import surface_decomposition
from compas_pattern.cad.rhino.draw import draw_mesh

srf_guid = rs.GetObject('get surface', filter=8)
discretisation = rs.GetReal('discretisation value', 1, 0)
decomposition = surface_decomposition(srf_guid, discretisation, output_delaunay=True, output_skeleton=False, output_mesh=False, output_polysurface=False)[0]
rs.EnableRedraw(False)
draw_mesh(decomposition)