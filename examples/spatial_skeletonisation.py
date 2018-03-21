import rhinoscriptsyntax as rs
from compas.utilities import XFunc
points = rs.GetObjects('pts', filter = 1)
points = [rs.PointCoordinates(pt) for pt in points]
points = [[xyz[0], xyz[1], xyz[2]] for xyz in points]

#from compas_pattern.algorithms.spatial_skeletonisation import spatial_skeleton_xfunc

simplices = XFunc('compas_pattern.algorithms.spatial_skeletonisation.spatial_skeleton_xfunc')(points)

rs.EnableRedraw(False)
for a, b, c, d in simplices:
    a, b, c, d = points[a], points[b], points[c], points[d]
    group = rs.AddGroup()
    lines = [rs.AddLine(a, b), rs.AddLine(a, c), rs.AddLine(a, d), rs.AddLine(b, c), rs.AddLine(b, d), rs.AddLine(c, d)]
    rs.AddObjectsToGroup(lines, group)
    from compas.geometry import centroid_points
    rs.AddPoint(centroid_points([a, b, c, d]))
    # sphere centre
rs.EnableRedraw(True)