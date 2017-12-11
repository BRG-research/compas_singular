import rhinoscriptsyntax as rs

from compas.datastructures.mesh import Mesh
import compas_rhino as rhino

from compas_pattern.topology.medial_axis import medial_axis_from_delaunay
from compas_pattern.algorithms.delaunay_to_qpd import delaunay_to_qpd

guid = rs.GetObject('get Delaunay mesh')
mesh = rhino.mesh_from_guid(Mesh, guid)

rs.EnableRedraw(False)

#medial_branches = medial_axis_from_delaunay(mesh)
medial_branches = delaunay_to_qpd(mesh)

for branch in medial_branches:
    rs.AddPolyline(branch)

rs.EnableRedraw(True)