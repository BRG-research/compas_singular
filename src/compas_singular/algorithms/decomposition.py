from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

from math import floor
# from math import ceil
from math import pi
from operator import itemgetter

from compas.geometry import Polyline
# from compas.geometry import length_vector
# from compas.geometry import length_vector_xy
from compas.geometry import subtract_vectors
from compas.geometry import angle_vectors
from compas.geometry import angle_vectors_signed
# from compas.geometry import cross_vectors
from compas.geometry import centroid_points
from compas.datastructures import trimesh_face_circle
from compas.datastructures import network_polylines
from compas.datastructures import mesh_insert_vertex_on_edge
from compas.datastructures import mesh_substitute_vertex_in_faces
from compas.datastructures import mesh_explode
from compas.datastructures import mesh_weld
from compas.datastructures import mesh_unweld_edges
from compas.utilities import pairwise
from compas.utilities import window
from compas.utilities import geometric_key

from ..datastructures import CoarsePseudoQuadMesh
from ..datastructures import Network
from ..datastructures import Skeleton
from ..datastructures import split_quad_in_pseudo_quads
from ..utilities import list_split

from .propagation import quadrangulate_mesh


__all__ = ['SkeletonDecomposition']


class SkeletonDecomposition(Skeleton):
    """SkeletonDecomposition class for the generate a coarse quad mesh based on a topological skeleton and its singularities.

    """

    def __init__(self):
        super(SkeletonDecomposition, self).__init__()
        self.mesh = None
        self.polylines = None
        self.relative_kink_angle_limit = pi / 8.
        self.flip_angle_limit = pi / 2.

    @classmethod
    def from_skeleton(cls, skeleton):
        """Construct a SkeletonDecomposition object from a Skeleton.

        Returns
        -------
        Skeleton
            A skeleton object.

        """
        return cls.from_vertices_and_faces(*skeleton.to_vertices_and_faces())

    @classmethod
    def from_mesh(cls, mesh):
        """Construct a SkeletonDecomposition object from a Mesh.

        Returns
        -------
        Skeleton
            A skeleton object.

        """
        return cls.from_vertices_and_faces(*mesh.to_vertices_and_faces())

    # --------------------------------------------------------------------------
    # key elements
    # --------------------------------------------------------------------------

    def corner_faces(self):
        """Get the indices of the corner faces in the Delaunay mesh, i.e. the ones with one neighbour.

        Returns
        -------
        list
            List of face keys.

        """
        return [fkey for fkey in self.faces() if len(self.face_neighbors(fkey)) == 1]

    def corner_vertices(self):
        """Get the indices of the corner vertices of the topological skeleton, i.e. the two-valent boundary vertices in the Delaunay mesh.

        Returns
        -------
        list
            List of vertex keys.

        """
        return [vkey for bdry in self.vertices_on_boundaries() for vkey in bdry if len(self.vertex_neighbors(vkey)) == 2]

    def split_vertices(self):
        """Get the indices of the boundary split vertices, i.e. the vertices of the singular faces.

        Returns
        -------
        list
            List of vertex keys.

        """
        return [vkey for fkey in self.singular_faces() for vkey in self.face_vertices(fkey)]

    # --------------------------------------------------------------------------
    # branches
    # --------------------------------------------------------------------------

    def branches_singularity_to_singularity(self):
        """Get the branch polylines of the topological skeleton between singularities only, not corners.

        Returns
        -------
        list
            List of polylines as list of point XYZ-coordinates.

        """
        map_corners = [geometric_key(trimesh_face_circle(self, corner)[0]) for corner in self.corner_faces()]
        return [
            branch for branch in self.branches()
            if geometric_key(branch[0]) not in map_corners and geometric_key(branch[-1]) not in map_corners]

    def branches_singularity_to_boundary(self):
        """Get new branch polylines between singularities and boundaries, at the location fo the split vertices. Not part of the topological skeleton.

        Returns
        -------
        list
            List of polylines as list of point XYZ-coordinates.

        """
        return [
            [trimesh_face_circle(self, fkey)[0], self.vertex_coordinates(vkey)]
            for fkey in self.singular_faces() for vkey in self.face_vertices(fkey)]

    def branches_boundary(self):
        """Get new branch polylines from the Delaunay mesh boundaries split at the corner and plit vertices. Not part of the topological skeleton.

        Returns
        -------
        list
            List of polylines as list of point XYZ-coordinates.

        """
        boundaries = [bdry + bdry[0:] for bdry in self.boundaries()]
        splits = self.corner_vertices() + self.split_vertices()
        split_boundaries = [split_boundary for boundary in boundaries for split_boundary in list_split(boundary, [boundary.index(split) for split in splits if split in boundary])]
        return [[self.vertex_coordinates(vkey) for vkey in boundary] for boundary in split_boundaries]

    # --------------------------------------------------------------------------
    # decomposition
    # --------------------------------------------------------------------------

    def decomposition_polylines(self):
        """Get all the branch polylines to form a decomposition of the Delaunay mesh.
        These branches include the ones between singularities, between singularities and boundaries and along boundaries.
        Additional branches for some fixes: the ones to further split boundaries that only have two splits.

        Returns
        -------
        list
            List of polylines as list of point XYZ-coordinates.

        """
        branches = self.branches_singularity_to_singularity() + self.branches_singularity_to_boundary() + self.branches_boundary()
        branches += self.branches_splitting_boundary_kinks()
        branches += self.branches_splitting_collapsed_boundaries()
        branches += self.branches_splitting_flipped_faces()
        self.polylines = network_polylines(Network.from_lines([(u, v) for polyline in branches for u, v in pairwise(polyline)]),
                                           splits=[self.vertex_coordinates(vkey) for vkey in self.corner_vertices()])
        return self.polylines

    def decomposition_polyline(self, geom_key_1, geom_key_2):
        """Retrieve the decomposition polyline with extremities corresponding to two geoemtric keys.

        Parameters
        ----------
        geom_key_1 : float
            Geometric key of one extremity.
        geom_key_2 : float
            Geometric key of the other extremity.

        Returns
        -------
        list, None
            A polyline as a list of point XYZ-coordinates if a polyline corresponds to the geometric keys, None otherwise.
        """
        polylines = {(geometric_key(polyline[0]), geometric_key(polyline[-1])): polyline for polyline in self.polylines}
        return polylines.get((geom_key_1, geom_key_2), polylines.get((geom_key_2, geom_key_1), None))

    def decomposition_mesh(self, poles):
        """Return a quad mesh based on the decomposition polylines.
        Some fixes are added to convert the mesh formed by the decomposition polylines into a (coarse) quad mesh.

        Returns
        -------
        mesh
            A coarse quad mesh based on the topological skeleton from a Delaunay mesh.

        """
        polylines = self.decomposition_polylines()
        boundary_keys = set([geometric_key(self.vertex_coordinates(vkey)) for bdry in self.vertices_on_boundaries() for vkey in bdry])
        boundary_polylines = [polyline for polyline in polylines if geometric_key(polyline[0]) in boundary_keys and geometric_key(polyline[1]) in boundary_keys]
        other_polylines = [polyline for polyline in polylines if geometric_key(polyline[0]) not in boundary_keys or geometric_key(polyline[1]) not in boundary_keys]
        self.mesh = CoarsePseudoQuadMesh.from_polylines(boundary_polylines, other_polylines)
        self.solve_triangular_faces()
        # self.quadrangulate_polygonal_faces()
        self.split_quads_with_poles(poles)
        self.store_pole_data(poles)
        return self.mesh

    # --------------------------------------------------------------------------
    # corrections
    # --------------------------------------------------------------------------

    def branches_splitting_collapsed_boundaries(self):
        """Add new branches to fix the problem of boundaries with less than three splits that would be collapsed in the decomposition mesh.

        Returns
        -------
        new_branches : list
            List of polylines as list of point XYZ-coordinates.

        """
        new_branches = []

        all_splits = set(list(self.corner_vertices()) + list(self.split_vertices()))

        for polyedge in [bdry + bdry[:1] for bdry in self.boundaries()]:

            splits = set([vkey for vkey in polyedge if vkey in all_splits])
            new_splits = []

            if len(splits) == 0:
                new_splits += [vkey for vkey in list(itemgetter(0, int(floor(len(polyedge) / 3)), int(floor(len(polyedge) * 2 / 3)))(polyedge))]

            elif len(splits) == 1:
                i = polyedge.index(splits[0])
                new_splits += list(itemgetter(i - int(floor(len(polyedge) * 2 / 3)), i - int(floor(len(polyedge) / 3)))(polyedge))

            elif len(splits) == 2:
                one, two = list_split(polyedge, [polyedge.index(vkey) for vkey in splits])
                half = one if len(one) > len(two) else two
                new_splits.append(half[int(floor(len(half) / 2))])

            for vkey in new_splits:
                fkey = list(self.vertex_faces(vkey))[0]
                for edge in self.face_halfedges(fkey):
                    if vkey in edge and not self.is_edge_on_boundary(*edge):
                        new_branches += [[trimesh_face_circle(self, fkey)[0], self.vertex_coordinates(vkey_2)] for vkey_2 in edge]
                        all_splits.update(edge)
                        break

        return new_branches

    def branches_splitting_flipped_faces(self):
        """Add new branches to fix the problem of polyline patches that would form flipped faces in the decomposition mesh.

        Returns
        -------
        new_branches : list
            List of polylines as list of point XYZ-coordinates.

        """
        new_branches = []
        centre_to_fkey = {geometric_key(trimesh_face_circle(self, fkey)[0]): fkey for fkey in self.faces()}

        # compute total rotation of polyline
        for polyline in self.branches_singularity_to_singularity():
            angles = [angle_vectors_signed(subtract_vectors(v, u), subtract_vectors(w, v), [0., 0., 1.]) for u, v, w in window(polyline, n=3)]
            # subdivide once per angle limit in rotation
            if abs(sum(angles)) > self.flip_angle_limit:
                # the step between subdivision points in polylines (+ 2 for the extremities, which will be discarded)
                alone = len(self.singular_faces()) == 0
                n = floor(abs(sum(angles)) / self.flip_angle_limit) + 1
                step = int(floor(len(polyline) / n))
                # add new branches from corresponding face in Delaunay mesh
                seams = polyline[:: step]
                if polyline[-1] != seams[-1]:
                    if len(seams) == n + 1:
                        del seams[-1]
                    seams.append(polyline[-1])
                if alone:
                    seams = seams[0:-1]
                else:
                    seams = seams[1:-1]
                for point in seams:
                    fkey = centre_to_fkey[geometric_key(point)]
                    for edge in self.face_halfedges(fkey):
                        if not self.is_edge_on_boundary(*edge):
                            new_branches += [[trimesh_face_circle(self, fkey)[0], self.vertex_coordinates(vkey)] for vkey in edge]
                            break

        return new_branches

    def branches_splitting_boundary_kinks(self):
        """Add new branches to fix the problem of boundary kinks not marked by the skeleton
        Due to a low density that did not spot the change of curvature at the kink.
        Does not modify the singularites on the contrarty to increasing the density.

        Returns
        -------
        new_branches : list
            List of polylines as list of point XYZ-coordinates.

        """
        new_branches = []

        singular_faces = set(self.singular_faces())
        for boundary in self.boundaries():
            angles = {(u, v, w): angle_vectors(subtract_vectors(self.vertex_coordinates(v), self.vertex_coordinates(u)), subtract_vectors(
                self.vertex_coordinates(w), self.vertex_coordinates(v))) for u, v, w in window(boundary + boundary[: 2], n=3)}
            for u, v, w, x, y in list(window(boundary + boundary[: 4], n=5)):

                # check if not a corner
                if self.vertex_degree(w) == 2:
                    continue

                angle = angles[(v, w, x)]
                adjacent_angles = (angles[(u, v, w)] + angles[(w, x, y)]) / 2

                if angle - adjacent_angles > self.relative_kink_angle_limit:
                    # check if not already marked via an adjacent singular face
                    if all([fkey not in singular_faces for fkey in self.vertex_faces(w)]):
                        fkeys = list(self.vertex_faces(w, ordered=True))
                        fkey = fkeys[int(floor(len(fkeys) / 2))]
                        for edge in self.face_halfedges(fkey):
                            if w in edge and not self.is_edge_on_boundary(*edge):
                                new_branches += [[trimesh_face_circle(self, fkey)[0], self.vertex_coordinates(vkey)] for vkey in edge]
                                break

        return new_branches

    def solve_triangular_faces(self):
        """Modify the decomposition mesh from polylines to make it a quad mesh by converting the degenerated quad faces that appear as triangular faces.
        """
        mesh = self.mesh

        for fkey in list(mesh.faces()):
            if len(mesh.face_vertices(fkey)) == 3:

                boundary_vertices = [vkey for vkey in mesh.face_vertices(fkey) if mesh.is_vertex_on_boundary(vkey)]
                case = sum(mesh.is_vertex_on_boundary(vkey) for vkey in mesh.face_vertices(fkey))

                if case == 1:
                    # convert triangular face to quad by duplicating the boundary vertex
                    # due to singular face vertices at the same location
                    u = boundary_vertices[0]
                    v = mesh.add_vertex(attr_dict={attr: xyz for attr, xyz in zip(['x', 'y', 'z'], mesh.vertex_coordinates(u))})

                    # modify adjacent faces
                    vertex_faces = mesh.vertex_faces(u, ordered=True)
                    mesh_substitute_vertex_in_faces(mesh, u, v, vertex_faces[: vertex_faces.index(fkey)])

                    # modify triangular face
                    mesh_insert_vertex_on_edge(mesh, u, mesh.face_vertex_ancestor(fkey, u), v)

                elif case == 2:
                    # remove triangular face and merge the two boundary vertices
                    # due to singularities at the same location
                    polyline = Polyline(self.decomposition_polyline(*map(lambda x: geometric_key(mesh.vertex_coordinates(x)), boundary_vertices)))
                    point = polyline.point(t=.5, snap=True)
                    new_vkey = mesh.add_vertex(attr_dict={'x': point.x, 'y': point.y, 'z': point.z})

                    # modify triangular face
                    mesh.delete_face(fkey)

                    # modify adjacent faces
                    for old_vkey in boundary_vertices:
                        mesh_substitute_vertex_in_faces(mesh, old_vkey, new_vkey, mesh.vertex_faces(old_vkey))
                        mesh.delete_vertex(old_vkey)

        to_move = {}
        # give some length to the new edge
        for edge in mesh.edges():
            threshold = 1e-6
            if mesh.edge_length(*edge) < threshold:
                for vkey in edge:
                    xyz = centroid_points([mesh.vertex_coordinates(nbr) for nbr in mesh.vertex_neighbors(vkey)])
                    xyz0 = mesh.vertex_coordinates(vkey)
                    to_move[vkey] = [0.1 * (a - a0) for a, a0 in zip(xyz, xyz0)]

        for vkey, xyz in to_move.items():
            attr = mesh.vertex[vkey]
            attr['x'] += xyz[0]
            attr['y'] += xyz[1]
            attr['z'] += xyz[2]

    def quadrangulate_polygonal_faces(self):
        # WIP: problem not all faces should have the same source for propagation
        supermesh = self.mesh

        delaunay_vertex_map = tuple(geometric_key(self.vertex_coordinates(vkey)) for vkey in self.vertices())
        # newly added vertices in mesh that were not in the Delaunay are missing...

        edges_to_unweld = [edge for edge in supermesh.edges() if sum([geometric_key(supermesh.vertex_coordinates(i)) in delaunay_vertex_map for i in edge]) == 2]
        mesh_unweld_edges(supermesh, edges_to_unweld)

        meshes = mesh_explode(supermesh)

        for mesh in meshes:
            candidate_map = {geometric_key(mesh.vertex_coordinates(vkey)): [] for vkey in mesh.vertices()}
            for vkey in mesh.vertices_on_boundaries():
                candidate_map[geometric_key(mesh.vertex_coordinates(vkey))].append(mesh.vertex_degree(vkey))

            source_map = tuple([geom_key for geom_key, valencies in candidate_map.items() if len(list(set(valencies))) > 1])
            self.mesh = mesh_weld(mesh)
            mesh = self.mesh

            sources = [vkey for vkey in mesh.vertices() if geometric_key(mesh.vertex_coordinates(vkey)) in source_map]

            quadrangulate_mesh(mesh, sources)

    def quadrangulate_polygonal_faces_wip(self):
        pass
        # mesh = self.mesh

        # delaunay_vertex_map = tuple(geometric_key(self.vertex_coordinates(vkey)) for vkey in self.vertices())

        # for fkey in mesh.faces():
        # 	face_vertices = mesh.face_vertices(fkey)
        # 	if len(face_vertices) > 4:

    def split_quads_with_poles(self, poles):
        new_lines = []

        mesh = self.mesh
        pole_map = tuple([geometric_key(pole) for pole in poles])

        faces = list(mesh.faces())
        for fkey in faces:
            fv = mesh.face_vertices(fkey)
            if len(fv) == 4:
                for vkey in fv:
                    if geometric_key(mesh.vertex_coordinates(vkey)) in pole_map:
                        idx = fv.index(vkey)
                        xkey = fv[idx + 2 - len(fv)]
                        new_lines.append([mesh.vertex_coordinates(vkey), mesh.vertex_coordinates(xkey)])
                        split_quad_in_pseudo_quads(mesh, fkey, vkey)
                        break

        self.polylines += new_lines
        return new_lines

    def store_pole_data(self, poles):
        mesh = self.mesh
        pole_map = tuple([geometric_key(pole) for pole in poles])

        face_poles = {}
        for fkey in mesh.faces():
            if len(mesh.face_vertices(fkey)) == 3:
                for vkey in mesh.face_vertices(fkey):
                    if geometric_key(mesh.vertex_coordinates(vkey)) in pole_map:
                        face_poles[fkey] = vkey
                        break
                if fkey not in face_poles:
                    print('pole missing')

        mesh.attributes['face_pole'] = face_poles

# ==============================================================================
# Main
# ==============================================================================


if __name__ == '__main__':
    pass
