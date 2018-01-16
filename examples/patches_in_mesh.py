import rhinoscriptsyntax as rs

from compas.datastructures.mesh import Mesh
import compas_rhino as rhino

from compas_pattern.topology.polyline_extraction import singularity_polylines

mesh = rs.GetObject('mesh', filter = 32)
mesh = rhino.mesh_from_guid(Mesh, mesh)

rs.EnableRedraw(False)

polylines = singularity_polylines(mesh)

polyline_guids = [rs.AddPolyline([mesh.vertex_coordinates(vkey) for vkey in polyline]) for polyline in polylines]

layer_name = 'patches_in_mesh'
rs.AddLayer(layer_name)
rs.ObjectLayer(polyline_guids, layer = layer_name)

rs.EnableRedraw(True)