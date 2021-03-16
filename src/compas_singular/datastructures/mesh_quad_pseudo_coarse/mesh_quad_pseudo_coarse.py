from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

from compas.geometry import Polyline
from compas.geometry import discrete_coons_patch
from compas.datastructures import meshes_join_and_weld
from compas.utilities import geometric_key
from compas.utilities import pairwise
from compas.utilities import linspace

from ..mesh_quad_coarse import CoarseQuadMesh
from ..mesh_quad_pseudo import PseudoQuadMesh


__all__ = [	'CoarsePseudoQuadMesh']


class CoarsePseudoQuadMesh(PseudoQuadMesh, CoarseQuadMesh):

    def __init__(self):
        super(CoarsePseudoQuadMesh, self).__init__()

    def densification(self, edges_to_curves=None):
        """Generate a denser quad mesh from the coarse quad mesh and its strip densities.

        Returns
        -------
        QuadMesh
            A denser quad mesh.
        edges_to_curves : dict, optional
            A dictionary with edges (u, v) pointing to curve for densification. The curves are lists of XYZ points.

        """

        edge_strip = {}
        for strip, edges in self.strips(data=True):
            for u, v in edges:
                edge_strip[u, v] = strip
                edge_strip[v, u] = strip

        pole_map = [geometric_key(self.vertex_coordinates(pole)) for pole in self.poles()]

        meshes = []
        for fkey in self.faces():
            polylines = []
            for u, v in self.face_halfedges(fkey):
                d = self.get_strip_density(edge_strip[u, v])

                if edges_to_curves:
                    polyline = []
                    if (u, v) in edges_to_curves:
                        curve = Polyline(edges_to_curves[u, v])
                        polyline = [curve.point(t) for t in linspace(0, 1, d)]
                    else:
                        curve = Polyline(edges_to_curves[v, u])
                        polyline = [curve.point(t) for t in linspace(0, 1, d)]
                        polyline[:] = polyline[::-1]
                else:
                    polyline = []
                    curve = Polyline([self.vertex_coordinates(u), self.vertex_coordinates(v)])
                    for i in range(0, d + 1):
                        point = curve.point(float(i) / float(d))
                        polyline.append(point)

                polylines.append(polyline)

            if self.is_face_pseudo_quad(fkey):
                pole = self.attributes['face_pole'][fkey]
                idx = self.face_vertices(fkey).index(pole)
                polylines.insert(idx, None)

            ab, bc, cd, da = polylines

            if cd:
                dc = cd[::-1]
            else:
                dc = None

            if da:
                ad = da[::-1]
            else:
                ad = None

            vertices, faces = discrete_coons_patch(ab, bc, dc, ad)
            faces = [[u for u, v in pairwise(face + face[:1]) if u != v] for face in faces]
            mesh = PseudoQuadMesh.from_vertices_and_faces_with_face_poles(vertices, faces)
            meshes.append(mesh)

        face_pole_map = {}
        for mesh in meshes:
            for fkey in mesh.faces():
                for u, v in pairwise(mesh.face_vertices(fkey) + mesh.face_vertices(fkey)[: 1]):
                    if geometric_key(mesh.vertex_coordinates(u)) in pole_map and geometric_key(mesh.vertex_coordinates(u)) == geometric_key(mesh.vertex_coordinates(v)):
                        face_pole_map[geometric_key(mesh.face_center(fkey))] = geometric_key(mesh.vertex_coordinates(u))
                        break

        self.set_quad_mesh(meshes_join_and_weld(meshes))

        face_pole = {}
        for fkey in self.get_quad_mesh().faces():
            if geometric_key(self.get_quad_mesh().face_center(fkey)) in face_pole_map:
                for vkey in self.get_quad_mesh().face_vertices(fkey):
                    if geometric_key(self.get_quad_mesh().vertex_coordinates(vkey)) == face_pole_map[geometric_key(self.get_quad_mesh().face_center(fkey))]:
                        face_pole[fkey] = vkey
                        break

        self.get_quad_mesh().attributes['face_pole'] = face_pole
        return self.get_quad_mesh()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':
    pass

    # import compas
    # from compas_singular.datastructures.mesh_quad_pseudo_coarse.mesh_quad_pseudo_coarse import CoarsePseudoQuadMesh
    # from compas.datastructures import mesh_weld
    # from compas_plotters.meshplotter import MeshPlotter

    # mesh = CoarsePseudoQuadMesh.from_json('/Users/Robin/Downloads/coarse_mesh_for_robin.json')
    # # # plotter = MeshPlotter(mesh, figsize=(20, 20))
    # # # plotter.draw_vertices(radius=0.4, text='key')
    # # # plotter.draw_edges()
    # # # plotter.draw_faces(text='key')
    # # # plotter.show()

    # data = {}
    # for key, value in mesh.attributes['face_pole'].items():
    #     data[int(key)] = value
    # mesh.attributes['face_pole'] = data
    # # #print(mesh.attributes['face_pole'][str(4)])

    # mesh.collect_strips()
    # mesh.set_strips_density(2)
    # mesh.densification()
    # dense_mesh = mesh.get_quad_mesh()
    # mesh.set_quad_mesh(mesh_weld(dense_mesh, precision='1f'))
    # dense_mesh = mesh.get_quad_mesh()
    # # # print(mesh_weld(dense_mesh, precision='2f').is_manifold())
    # print(mesh.is_manifold())
    # print(dense_mesh.is_manifold())
    # # # geom_key_map = [geometric_key(dense_mesh.vertex_coordinates(vkey), precision='2f') for vkey in dense_mesh.vertices()]
    # # # for key in geom_key_map:
    # # # 	if geom_key_map.count(key) > 1:
    # # # 		print(geom_key_map)
    # # # for key in dense_mesh.vertices():
    # # # 	#if list(dense_mesh.halfedge[key].values()).count(None) > 1:
    # # # 	#	print(key, dense_mesh.halfedge[key])
    # # # 	if len(dense_mesh.vertex_neighbors(key)) > 4:
    # # # 		print(key, dense_mesh.vertex_neighbors(key))
    # print(dense_mesh.boundaries())
    # # plotter = MeshPlotter(mesh.get_quad_mesh(), figsize=(20, 20))
    # # plotter.draw_vertices(radius=0.4)#, text='key')
    # # plotter.draw_edges()
    # # plotter.draw_faces()
    # # plotter.show()

    # # vertices = [
    # # 	[0, 0, 0],
    # # 	[1, 0, 0],
    # # 	[2, 0, 0],
    # # 	[2, 1, 0],
    # # 	[1, 1, 0],
    # # 	[0, 1, 0]
    # # ]

    # # faces = [
    # # 	[0, 1, 4, 5],
    # # 	[1, 2, 3, 4]
    # # ]

    # # mesh = CoarsePseudoQuadMesh.from_vertices_and_faces(vertices, faces)
    # # mesh.collect_strips()
    # # mesh.set_strips_density(2)
    # # mesh.densification()

    # # print(mesh.get_quad_mesh().is_manifold())
