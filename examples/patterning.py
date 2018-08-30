import rhinoscriptsyntax as rs

from compas.datastructures.mesh import Mesh
import compas_rhino as rhino

from compas_pattern.topology.pattern_operators import conway_ambo

from compas_pattern.cad.rhino.utilities import draw_mesh

mesh = rs.GetObject('mesh', filter = 32)
mesh = rhino.mesh_from_guid(Mesh, mesh)

mesh = conway_ambo(mesh)

rs.EnableRedraw(False)
draw_mesh(mesh)
rs.EnableRedraw(True)