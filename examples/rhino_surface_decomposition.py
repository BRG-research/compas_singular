import rhinoscriptsyntax as rs
from compas_pattern.algorithms.decomposition.algorithm import surface_decomposition
from compas_pattern.algorithms.decomposition.algorithm import decomposition_curves
from compas_pattern.algorithms.decomposition.algorithm import decomposition_mesh

from compas_rhino.artists import MeshArtist

guids = rs.GetObjects('get surfaces', filter=8)
crv_guids = rs.GetObjects('get curves', filter=4) or []
pt_guids = rs.GetObjects('get points', filter=1) or []
discretisation = rs.GetReal('discretisation value', 1, 0)
box = rs.BoundingBox(guids)
scale = rs.Distance(box[0], box[2])
#discretisation = 0.005 * scale
rs.EnableRedraw(False)
for srf_guid in guids:
    decomposition, outer_boundary, inner_boundaries, polyline_features, point_features = surface_decomposition(srf_guid, discretisation, crv_guids = crv_guids, pt_guids = pt_guids)
    mesh = decomposition_mesh(srf_guid, decomposition, point_features)
    rs.EnableRedraw(False)
    MeshArtist(mesh).draw_mesh()
    #for u, v in mesh.edges():
    #    rs.AddLine(mesh.vertex_coordinates(u), mesh.vertex_coordinates(v))