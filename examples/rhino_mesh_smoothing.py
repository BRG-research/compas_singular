import rhinoscriptsyntax as rs
from compas_rhino.geometry import RhinoMesh
from compas_pattern.cad.rhino.objects.surface import RhinoSurface
from compas_pattern.datastructures.mesh.mesh import Mesh
from compas_pattern.algorithms.relaxation.constraints import automated_smoothing_constraints
from compas_pattern.algorithms.relaxation.constraints import automated_smoothing_surface_constraints
from compas_pattern.algorithms.relaxation.relaxation import constrained_smoothing
from compas_pattern.cad.rhino.draw import draw_mesh

guid = rs.GetObject('get mesh', filter = 32)
srf_guid = rs.GetObject('get surface', filter = 8)
crv_guids = rs.GetObjects('get curves', filter = 4)
pt_guids = rs.GetObjects('get points', filter = 1)
rs.EnableRedraw(False)
mesh = Mesh.from_vertices_and_faces(*RhinoMesh.from_guid(guid).get_vertices_and_faces())

if srf_guid is not None:
    constraints = automated_smoothing_surface_constraints(mesh, RhinoSurface(srf_guid))
else:
    constraints = {}
    
for vkey in mesh.vertices():
    if not mesh.is_vertex_on_boundary(vkey):
        for crv_guid in crv_guids:
            if rs.IsPointOnCurve(crv_guid, mesh.vertex_coordinates(vkey)):
                constraints[vkey] = crv_guid
                break

constraints.update(automated_smoothing_constraints(mesh, pt_guids))

kmax = rs.GetInteger('number of smoothing iterations?', 20, 0, 100)
damping = rs.GetReal('value of smoothing damping?', 0.5, 0, 1)

count = 100
while count:
    count -=1
    constrained_smoothing(mesh, kmax = kmax, damping = damping, constraints = constraints, algorithm = 'area')
    guid = draw_mesh(mesh)
    bool = rs.GetString('more smoothing?', 'False', ['True', 'False'])
    if bool == 'False':
        break
    rs.DeleteObject(guid)
