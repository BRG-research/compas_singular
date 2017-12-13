import rhinoscriptsyntax as rs

from compas.datastructures.mesh import Mesh
import compas_rhino as rhino

from compas_pattern.topology.medial_axis import medial_axis_from_delaunay
from compas_pattern.algorithms.delaunay_to_qpd import delaunay_to_patch_decomposition
from compas_pattern.topology.mesh_boundary_polylines import mesh_boundaries

#guid = rs.GetObject('get Delaunay mesh')
#mesh = rhino.mesh_from_guid(Mesh, guid)

mesh = Mesh.from_json('rolex_learning_centre.json')

rs.EnableRedraw(False)

patch_decomposition = delaunay_to_patch_decomposition(mesh)

for vertices in patch_decomposition:
    rs.AddPolyline(vertices)

rs.EnableRedraw(True)