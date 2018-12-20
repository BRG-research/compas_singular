import rhinoscriptsyntax as rs

from compas_pattern.topology.weaving import Weaving
from compas_pattern.cad.rhino.utilities import draw_mesh

lines = [
([0., 0., 0.],[1., 0., -1.]),
([0., 0., 0.],[-1., 0., -1.]),
([0., 0., 0.],[0., 1., -1.]),
([0., 0., 0.],[0., -1., -1.]),
([0., 0., 0.],[0., 0., 1.]),
]

rs.EnableRedraw(False)

weaving = Weaving.from_lines(lines)
weaving.densification(2)
weaving.patterning()

polylines = [rs.AddPolyline(polyline) for polyline in weaving.kagome_polylines()]

#polylines = [rs.AddPolyline(polygon + polygon[:1]) for polygon in weaving.weaving_negative_polygons()]
#rs.ObjectColor(polylines, [0,0,255])

#colours = [[255,0,0], [0,255,0], [0,0,255], [0,255,255], [255,0,255], [255,255,0], [0,0,0],[255,255,255]]
#for polyline, colour in weaving.kagome_polyline_colouring().items():
#    guid = rs.AddPolyline(polyline)
#    rs.ObjectColor(guid, colours[colour])

#draw_mesh(weaving.kagome)
rs.EnableRedraw(True)