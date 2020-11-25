from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

from copy import deepcopy
from math import floor
from math import ceil

from compas.datastructures import meshes_join_and_weld
from compas.topology import adjacency_from_edges
from compas.topology import connected_components
from compas.geometry import discrete_coons_patch
from compas.geometry import vector_average
from compas.utilities import pairwise

from ..mesh import Mesh
from ..mesh_quad import QuadMesh


__all__ = ['CoarseQuadMesh']


class CoarseQuadMesh(QuadMesh):

    def __init__(self):
        super(CoarseQuadMesh, self).__init__()
        self.attributes['strips_density'] = {}
        self.attributes['vertex_coarse_to_dense'] = {}
        self.attributes['edge_coarse_to_dense'] = {}
        self.attributes['quad_mesh'] = None
        self.attributes['polygonal_mesh'] = None

    # --------------------------------------------------------------------------
    # constructors
    # --------------------------------------------------------------------------

    @classmethod
    def from_quad_mesh(cls, quad_mesh, collect_strips=True, collect_polyedges=True, attribute_density=True):
        """Build coarse quad mesh from quad mesh with density and child-parent element data.

        Parameters
        ----------
        quad_mesh : QuadMesh
            A quad mesh.
        attribute_density : bool, optional
            Keep density data of dense quad mesh and inherit it as aatribute.

        Returns
        ----------
        coarse_quad_mesh : CoarseQuadMesh
            A coarse quad mesh with density data.
        """
        polyedges = quad_mesh.singularity_polyedge_decomposition()

        # vertex data
        vertices = {vkey: quad_mesh.vertex_coordinates(vkey) for vkey in quad_mesh.vertices()}
        coarse_vertices_children = {vkey: vkey for polyedge in polyedges for vkey in [polyedge[0], polyedge[-1]]}
        coarse_vertices = {vkey: quad_mesh.vertex_coordinates(vkey) for vkey in coarse_vertices_children}

        # edge data
        coarse_edges_children = {(polyedge[0], polyedge[-1]): polyedge for polyedge in polyedges}
        singularity_edges = [(x, y) for polyedge in polyedges for u, v in pairwise(polyedge) for x, y in [(u, v), (v, u)]]

        # face data
        faces = {fkey: quad_mesh.face_vertices(fkey) for fkey in quad_mesh.faces()}
        adj_edges = {(f1, f2) for f1 in quad_mesh.faces() for f2 in quad_mesh.face_neighbors(f1) if f1 < f2 and quad_mesh.face_adjacency_halfedge(f1, f2) not in singularity_edges}
        coarse_faces_children = {}
        for i, connected_faces in enumerate(connected_components(adjacency_from_edges(adj_edges))):
            mesh = Mesh.from_vertices_and_faces(vertices, [faces[face] for face in connected_faces])
            coarse_faces_children[i] = [vkey for vkey in reversed(mesh.boundaries()[0]) if mesh.vertex_degree(vkey) == 2]

        coarse_quad_mesh = cls.from_vertices_and_faces(coarse_vertices, coarse_faces_children)

        # attribute relation child-parent element between coarse and dense quad meshes
        coarse_quad_mesh.attributes['vertex_coarse_to_dense'] = coarse_vertices_children
        coarse_quad_mesh.attributes['edge_coarse_to_dense'] = {u: {} for u in coarse_quad_mesh.vertices()}
        for (u, v), polyedge in coarse_edges_children.items():
            coarse_quad_mesh.attributes['edge_coarse_to_dense'][u][v] = polyedge
            coarse_quad_mesh.attributes['edge_coarse_to_dense'][v][u] = list(reversed(polyedge))

        # collect strip and polyedge attributes
        if collect_strips:
            coarse_quad_mesh.collect_strips()
        if collect_polyedges:
            coarse_quad_mesh.collect_polyedges()

        # store density attribute from input dense quad mesh
        if attribute_density:
            coarse_quad_mesh.set_strips_density(1)
            for skey in coarse_quad_mesh.strips():
                u, v = coarse_quad_mesh.strip_edges(skey)[0]
                d = len(coarse_edges_children.get((u, v), coarse_edges_children.get((v, u), [])))
                coarse_quad_mesh.set_strip_density(skey, d)

        # store quad mesh and use as polygonal mesh
        coarse_quad_mesh.set_quad_mesh(quad_mesh)
        coarse_quad_mesh.set_polygonal_mesh(deepcopy(quad_mesh))

        return coarse_quad_mesh

    # --------------------------------------------------------------------------
    # meshes getters and setters
    # --------------------------------------------------------------------------

    def get_quad_mesh(self):
        return self.attributes['quad_mesh']

    def set_quad_mesh(self, quad_mesh):
        self.attributes['quad_mesh'] = quad_mesh

    def get_polygonal_mesh(self):
        return self.attributes['polygonal_mesh']

    def set_polygonal_mesh(self, polygonal_mesh):
        self.attributes['polygonal_mesh'] = polygonal_mesh

    # --------------------------------------------------------------------------
    # element child-parent relation getters
    # --------------------------------------------------------------------------

    def coarse_edge_dense_edges(self, u, v):
        """Return the child edges, or polyedge, in the dense quad mesh from a parent edge in the coarse quad mesh."""
        return self.attributes['edge_coarse_to_dense'][u][v]

    # --------------------------------------------------------------------------
    # density getters and setters
    # --------------------------------------------------------------------------

    def get_strip_density(self, skey):
        """Get the density of a strip.

        Parameters
        ----------
        skey : hashable
            A strip key.

        Returns
        ----------
        int
            The strip density.
        """
        return self.attributes['strips_density'][skey]

    def get_strip_densities(self):
        """Get the density of a strip.

        Returns
        ----------
        dict
            The dictionary of the strip densities.
        """
        return self.attributes['strips_density']

    # --------------------------------------------------------------------------
    # density setters
    # --------------------------------------------------------------------------

    def set_strip_density(self, skey, d):
        """Set the densty of one strip.

        Parameters
        ----------
        skey : hashable
            A strip key.
        d : int
            A density parameter.
        """
        self.attributes['strips_density'][skey] = d

    def set_strips_density(self, d, skeys=None):
        """Set the same density to all strips.

        Parameters
        ----------
        d : int
            A density parameter.
        skeys : list, None
            The keys of strips to set density. If is None, all strips are considered.
        """
        if skeys is None:
            skeys = self.strips()
        for skey in skeys:
            self.set_strip_density(skey, d)

    def set_strip_density_target(self, skey, t):
        """Set the strip densities based on a target length and the average length of the strip edges.

        Parameters
        ----------
        skey : hashable
            A strip key.
        t : float
            A target length.
        """
        self.set_strip_density(skey, int(ceil(vector_average([self.edge_length(u, v) for u, v in self.strip_edges(skey) if u != v]) / t)))

    def set_strip_density_func(self, skey, func, func_args):
        """Set the strip densities based on a function.

        Parameters
        ----------
        skey : hashable
            A strip key.
        """
        self.set_strip_density(skey, int(func(skey, func_args)))

    def set_strips_density_target(self, t, skeys=None):
        """Set the strip densities based on a target length and the average length of the strip edges.

        Parameters
        ----------
        t : float
            A target length.
        skeys : list, None
            The keys of strips to set density. If is None, all strips are considered.
        """
        if skeys is None:
            skeys = self.strips()
        for skey in skeys:
            self.set_strip_density_target(skey, t)

    def set_strips_density_func(self, func, func_args, skeys=None):
        """Set the strip densities based on a function.

        Parameters
        ----------
        skeys : list, None
            The keys of strips to set density. If is None, all strips are considered.
        """
        if skeys is None:
            skeys = self.strips()
        for skey in skeys:
            self.set_strip_density_func(skey, func, func_args)

    def set_mesh_density_face_target(self, nb_faces):
        """Set equal strip densities based on a target number of faces.

        Parameters
        ----------
        nb_faces : int
            The target number of faces.
        """
        n = (nb_faces / self.number_of_faces()) ** .5
        if ceil(n) - n > n - floor(n):
            n = int(floor(n))
        else:
            n = int(ceil(n))
        self.set_strips_density(n)

    # --------------------------------------------------------------------------
    # densification
    # --------------------------------------------------------------------------

    def densification(self):
        """Generate a denser quad mesh from the coarse quad mesh and its strip densities.
        """
        edge_strip = {}
        for skey, edges in self.strips(data=True):
            for edge in edges:
                edge_strip[edge] = skey
                edge_strip[tuple(reversed(edge))] = skey

        face_meshes = {}
        for fkey in self.faces():
            ab, bc, cd, da = [[self.edge_point(u, v, float(i) / float(self.get_strip_density(edge_strip[(u, v)])))
                               for i in range(0, self.get_strip_density(edge_strip[(u, v)]) + 1)] for u, v in self.face_halfedges(fkey)]
            vertices, faces = discrete_coons_patch(ab, bc, list(reversed(cd)), list(reversed(da)))
            face_meshes[fkey] = QuadMesh.from_vertices_and_faces(vertices, faces)

        self.set_quad_mesh(meshes_join_and_weld(list(face_meshes.values())))

    # def geometrical_densification(self):
    # 	"""Generate a denser quad mesh from the coarse quad mesh and its strip densities.

    # 	WIP!

    # 	Returns
    # 	-------
    # 	QuadMesh
    # 		A denser quad mesh.

    # 	"""

    # 	if self.quad_mesh is None:
    # 		self.quad_mesh = self.copy()
    # 		self.polygonal_mesh = self.copy()
    # 		self.vertex_to_vertex = {vkey: vkey for vkey in self.vertices()}

    # 		self.edge_to_polyedge = {vkey: {} for vkey in self.vertices()}
    # 		for u, v in self.edges():
    # 			self.edge_to_polyedge[u][v] = (u, v)
    # 			self.edge_to_polyedge[v][u] = (v, u)

    # 	quad_mesh = self.quad_mesh

    # 	new_edge_polyline = {}

    # 	for u, v in self.edges():
    # 		d =  self.get_strip_density(self.edge_strip((u, v)))
    # 		old_polyline = Polyline([quad_mesh.vertex_coordinates(vkey) for vkey in self.edge_to_polyedge[u][v]])
    # 		new_polyline = [old_polyline.point(float(i) / float(d)) for i in range(0, d + 1)]
    # 		new_edge_polyline[(u, v)] = new_polyline
    # 		new_edge_polyline[(v, u)] = list(reversed(new_polyline))

    # 	meshes = []

    # 	new_edge_polyedge = {}
    # 	new_vertex_vertex = {}

    # 	for i, fkey in enumerate(self.faces()):
    # 		ab, bc, cd, da = [new_edge_polyline[edge] for edge in self.face_halfedges(fkey)]

    # 		a, b, c, d = self.face_vertices(fkey)
    # 		n, m = len(ab), len(bc)
    # 		vertices, faces = discrete_coons_patch(ab, bc, list(reversed(cd)), list(reversed(da)))
    # 		meshes.append(QuadMesh.from_vertices_and_faces(vertices, faces))
    # 		ab, bc, cd, da = list(self.face_halfedges(fkey))

    # 		new_edge_polyedge[ab] = [i, range(0, m)]
    # 		new_edge_polyedge[tuple(reversed(ab))] = [new_edge_polyedge[ab][0], list(reversed(new_edge_polyedge[ab][1]))]

    # 		new_edge_polyedge[bc] = [i, range(m - 1, n * m, m)]
    # 		new_edge_polyedge[tuple(reversed(bc))] = [new_edge_polyedge[bc][0], list(reversed(new_edge_polyedge[bc][1]))]

    # 		new_edge_polyedge[cd] = [i, list(reversed(range((n - 1) * m, n * m)))]
    # 		new_edge_polyedge[tuple(reversed(cd))] = [new_edge_polyedge[cd][0], list(reversed(new_edge_polyedge[cd][1]))]

    # 		new_edge_polyedge[da] = [i, list(reversed(range(0, (n - 1) * m + 1, m)))]
    # 		new_edge_polyedge[tuple(reversed(da))] = [new_edge_polyedge[da][0], list(reversed(new_edge_polyedge[da][1]))]

    # 		new_vertex_vertex[a] = (new_edge_polyedge[ab][0], new_edge_polyedge[ab][1][0])
    # 		new_vertex_vertex[b] = (new_edge_polyedge[ab][0], new_edge_polyedge[ab][1][-1])
    # 		new_vertex_vertex[c] = (new_edge_polyedge[cd][0], new_edge_polyedge[cd][1][0])
    # 		new_vertex_vertex[d] = (new_edge_polyedge[cd][0], new_edge_polyedge[cd][1][-1])

    # 	self.quad_mesh, old_to_new_vertices = meshes_join_and_weld(meshes, data = True)

    # 	self.vertex_to_vertex = {vkey: old_to_new_vertices[tuple(new_vertex_vertex[vkey])] for vkey in self.vertices()}

    # 	for u, v in self.edges():
    # 		i, vkeys = new_edge_polyedge[(u, v)]
    # 		new_polyedge = [old_to_new_vertices[(i, vkey)] for vkey in vkeys]

    # 		if self.vertex_to_vertex[u] == new_polyedge[0]:
    # 			self.edge_to_polyedge[u][v] = new_polyedge
    # 			self.edge_to_polyedge[v][u] = list(reversed(new_polyedge))

    # 		elif self.vertex_to_vertex[u] == new_polyedge[-1]:
    # 			self.edge_to_polyedge[u][v] = list(reversed(new_polyedge))
    # 			self.edge_to_polyedge[v][u] = new_polyedge

    # 		else:
    # 			pass

    # 	return self.quad_mesh


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':
    pass

    # import compas
    # from compas_singular.datastructures.mesh_quad.mesh_quad import QuadMesh
    # from compas.datastructures.mesh import mesh_smooth_centroid
    # from compas_plotters.meshplotter import MeshPlotter

    # #mesh = QuadMesh.from_obj(compas.get('faces.obj'))
    # # mesh = QuadMesh.from_json('/Users/Robin/Desktop/json/debug.json')
    # # mesh.collect_strips()
    # # mesh.collect_polyedges()

    # mesh_0 = CoarseQuadMesh.from_quad_mesh(QuadMesh.from_obj(compas.get('faces.obj')))
    # mesh_0.collect_strips()
    # # mesh_0.collect_polyedges()
    # # print(mesh_0.is_quadmesh())
    # # print(mesh_0.number_of_strips())

    # # vertices = [
    # [12.97441577911377, 24.33094596862793, 0.0], [18.310085296630859, 8.467333793640137, 0.0],
    # [30.052173614501953, 18.846050262451172, 0.0], [17.135400772094727, 16.750551223754883, 0.0],
    # [16.661802291870117, 22.973459243774414, 0.0], [14.180665969848633, 26.949295043945313, 0.0],
    # [36.052761077880859, 26.372636795043945, 0.0], [26.180931091308594, 21.778648376464844, 0.0],
    # [19.647378921508789, 12.288106918334961, 0.0], [9.355668067932129, 16.475896835327148, 0.0],
    # [18.929227828979492, 16.271940231323242, 0.0], [7.34525203704834, 12.111981391906738, 0.0],
    # [13.31309986114502, 14.699410438537598, 0.0], [18.699434280395508, 19.613750457763672, 0.0],
    # [11.913931846618652, 10.593378067016602, 0.0], [17.163223266601563, 26.870658874511719, 0.0],
    # [26.110898971557617, 26.634754180908203, 0.0], [22.851469039916992, 9.81414794921875, 0.0],
    # [21.051292419433594, 7.556171894073486, 0.0], [22.1370792388916, 19.089054107666016, 0.0]]
    # # faces = [
    # [15, 5, 0, 4], [0, 9, 12, 4], [9, 11, 14, 12], [14, 1, 8, 12], [1, 18, 17, 8], [17, 2, 7, 8],
    # [2, 6, 16, 7], [16, 15, 4, 7], [13, 19, 7, 4], [19, 10, 8, 7], [10, 3, 12, 8], [3, 13, 4, 12]]
    # # mesh = QuadMesh.from_vertices_and_faces(vertices, faces)
    # # mesh.collect_strips()
    # # mesh.collect_polyedges()

    # # mesh_0 = CoarseQuadMesh.from_quad_mesh(mesh)
    # # mesh_0.collect_strips()
    # # mesh_0.collect_polyedges()

    # # print(mesh_0.number_of_strips())
    # # print(mesh_0.attributes['vertex_coarse_to_dense'])
    # # print(mesh_0.attributes['edge_coarse_to_dense'])

    # # mesh_0.set_strips_density(1)
    # # mesh_0.set_strip_density(0, 6)
    # # mesh_0.set_strip_density(1, 5)
    # # mesh_0.densification()
    # # mesh_0.get_strip_densities()
    # #mesh_smooth_centroid(mesh_0.quad_mesh, kmax = 10)

    # # mesh_0.set_strips_density(10)
    # # mesh_0.densification()

    # plotter = MeshPlotter(mesh_0, figsize=(10, 10))
    # plotter.draw_edges()
    # plotter.draw_vertices()
    # plotter.draw_faces()
    # plotter.show()
