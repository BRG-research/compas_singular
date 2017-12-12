import rhinoscriptsyntax as rs

from compas.datastructures.mesh import Mesh
import compas_rhino as rhino

from compas_pattern.topology.medial_axis import medial_axis_from_delaunay
from compas_pattern.algorithms.delaunay_to_qpd import delaunay_to_patch_decompostion
from compas_pattern.topology.mesh_boundary_polylines import mesh_boundaries

guid = rs.GetObject('get Delaunay mesh')
mesh = rhino.mesh_from_guid(Mesh, guid)

rs.EnableRedraw(False)

#medial_branches = medial_axis_from_delaunay(mesh)
#medial_branches = delaunay_to_patch_decompostion(mesh)

boundaries = mesh_boundaries(mesh)
for boundary in boundaries:
    vertices = [mesh.vertex_coordinates(vkey) for vkey in boundary]
    rs.AddPolyline(vertices)

rs.EnableRedraw(True)