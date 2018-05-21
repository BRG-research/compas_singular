import rhinoscriptsyntax as rs
from compas.utilities import XFunc
points = rs.GetObjects('pts', filter = 1)
points = [rs.PointCoordinates(pt) for pt in points]
points = [[xyz[0], xyz[1], xyz[2]] for xyz in points]

#from compas_pattern.algorithms.spatial_skeletonisation import spatial_skeleton_xfunc

simplices, neighbors = XFunc('compas_pattern.algorithms.spatial_skeletonisation.spatial_skeleton_xfunc')(points)

#rs.EnableRedraw(False)
#for a, b, c, d in simplices:
#    a, b, c, d = points[a], points[b], points[c], points[d]
#    group = rs.AddGroup()
#    lines = [rs.AddLine(a, b), rs.AddLine(a, c), rs.AddLine(a, d), rs.AddLine(b, c), rs.AddLine(b, d), rs.AddLine(c, d)]
#    rs.AddObjectsToGroup(lines, group)
#    from compas.geometry import centroid_points
#    rs.AddPoint(centroid_points([a, b, c, d]))
#    # sphere centre
#rs.EnableRedraw(True)

cells = []
for a, b, c, d in simplices:
    #print a, b, c, d
    halffaces = [ [a, b, c], [a, b, d], [a, c, d], [b, c, d] ]
    cells.append(halffaces)
    #halffaces.append([a, b, c])
    #halffaces.append([c, b, a])
    #halffaces.append([a, b, d])
    #halffaces.append([d, b, a])
    #halffaces.append([a, c, d])
    #halffaces.append([d, c, a])
    #halffaces.append([b, c, d])
    #halffaces.append([d, c, d])


from compas.datastructures import VolMesh

volmesh = VolMesh.from_vertices_and_cells(points, cells)

print volmesh.cells()

#rs.EnableRedraw(False)
#for u, v in volmesh.edges():
#    u = volmesh.vertex_coordinates(u)
#    v = volmesh.vertex_coordinates(v)
#    rs.AddLine(u, v)
#rs.EnableRedraw(True)