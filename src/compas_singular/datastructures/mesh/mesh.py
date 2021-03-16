from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

from compas.datastructures import Mesh
from compas.geometry import centroid_points
from compas.geometry import angle_points
# from compas.utilities import geometric_key
# from compas.utilities import pairwise


__all__ = ['Mesh']


class Mesh(Mesh):

    def __init__(self):
        super(Mesh, self).__init__()

    def to_vertices_and_faces(self, keep_keys=True):

        if keep_keys:
            vertices = {vkey: self.vertex_coordinates(vkey) for vkey in self.vertices()}
            faces = {fkey: self.face_vertices(fkey) for fkey in self.faces()}
        else:
            key_index = self.key_index()
            vertices = [self.vertex_coordinates(key) for key in self.vertices()]
            faces = [[key_index[key] for key in self.face_vertices(fkey)] for fkey in self.faces()]
        return vertices, faces

    def boundaries(self):
        """Collect the mesh boundaries as lists of vertices.

        Parameters
        ----------
        mesh : Mesh
            Mesh.

        Returns
        -------
        boundaries : list
            List of boundaries as lists of vertex keys.

        """

        boundary_edges = {}
        for u, v in self.edges():
            if self.halfedge[u][v] is None:
                boundary_edges[u] = v
            elif self.halfedge[v][u] is None:
                boundary_edges[v] = u

        boundaries = []
        boundary = list(boundary_edges.popitem())
        while len(boundary_edges) > 0:
            w = boundary_edges.pop(boundary[-1])
            if w == boundary[0]:
                boundaries.append(boundary)
                if len(boundary_edges) > 0:
                    boundary = list(boundary_edges.popitem())
            else:
                boundary.append(w)

        return boundaries

    def is_boundary_vertex_kink(self, vkey, threshold_angle):
        """Return whether there is a kink at a boundary vertex according to a threshold angle.

        Parameters
        ----------
        vkey : Key
            The boundary vertex key.
        threshold_angle : float
            Threshold angle in rad.

        Returns
        -------
        bool
            True if vertex is on the boundary and has an angle larger than the threshold angle. False otherwise.
        """

        # check if vertex is on boundary
        if not self.is_vertex_on_boundary(vkey):
            return False

        # get the two adjacent boundary vertices (exactly two for manifold meshes)
        ukey, wkey = [nbr for nbr in self.vertex_neighbors(vkey) if self.is_edge_on_boundary(vkey, nbr)]

        # compare boundary angle with threshold angle
        return angle_points(self.vertex_coordinates(ukey), self.vertex_coordinates(vkey), self.vertex_coordinates(wkey)) > threshold_angle

    def boundary_kinks(self, threshold_angle):
        """Return the boundary vertices with kinks.

        Parameters
        ----------
        threshold_angle : float
            Threshold angle in rad.

        Returns
        -------
        list
            The list of the boundary vertices at kink angles higher than the threshold value.

        """

        return [vkey for bdry in self.vertices_on_boundaries() for vkey in bdry if self.is_boundary_vertex_kink(vkey, threshold_angle)]

    def vertex_centroid(self):
        """Calculate the centroid of the mesh vertices.

        Parameters
        ----------

        Returns
        -------
        list
            The coordinates of the centroid of the mesh vertices.
        """

        return centroid_points([self.vertex_coordinates(vkey) for vkey in self.vertices()])


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':
    pass
