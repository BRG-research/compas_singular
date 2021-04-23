from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

from math import floor
from operator import itemgetter

from compas.geometry import centroid_points
from compas.utilities import pairwise

from compas_singular.utilities import list_split

from ..mesh import Mesh


__all__ = ['QuadMesh']


class QuadMesh(Mesh):

    def __init__(self):
        super(QuadMesh, self).__init__()
        self.attributes['strips'] = {}
        self.attributes['polyedges'] = {}

    def strips(self, data=False):

        for skey in self.attributes['strips']:
            if data:
                yield skey, self.attributes['strips'][skey]
            else:
                yield skey

    def polyedges(self, data=False):
        for key in self.attributes['polyedges']:
            if data:
                yield key, self.attributes['polyedges'][key]
            else:
                yield key

    # --------------------------------------------------------------------------
    # opposite elements
    # --------------------------------------------------------------------------

    def face_opposite_edge(self, u, v):
        """Returns the opposite edge in the quad face.

        Parameters
        ----------
        u : int
            The identifier of the edge start.
        v : int
            The identifier of the edge end.

        Returns
        -------
        (w, x) : tuple
            The opposite edge.

        """

        fkey = self.halfedge[u][v]
        w = self.face_vertex_descendant(fkey, v)
        x = self.face_vertex_descendant(fkey, w)
        return (w, x)

    def vertex_opposite_vertex(self, u, v):
        """Returns the opposite vertex to u accross vertex v.

        Parameters
        ----------
        u : hashable
            A vertex key.
        v : hashable
            A vertex key.

        Returns
        -------
        hashable, None
            The opposite vertex.
            None if v is a singularity or if (u, v) leads outwards.

        """

        if self.is_vertex_singular(v):
            return None

        elif self.is_vertex_on_boundary(v):

            if not self.is_vertex_on_boundary(u):
                return None

            else:
                return [nbr for nbr in self.vertex_neighbors(v) if nbr != u and self.is_vertex_on_boundary(nbr)][0]

        else:
            nbrs = self.vertex_neighbors(v, ordered=True)
            return nbrs[nbrs.index(u) - 2]

    # --------------------------------------------------------------------------
    # singularities
    # --------------------------------------------------------------------------

    def is_vertex_singular(self, vkey):
        """Output whether a vertex is quad mesh singularity.

        Parameters
        ----------
        vkey : int
            The vertex key.

        Returns
        -------
        bool
            True if the vertex is a quad mesh singularity. False otherwise.

        """

        if (self.is_vertex_on_boundary(vkey) and self.vertex_degree(vkey) != 3) or (not self.is_vertex_on_boundary(vkey) and self.vertex_degree(vkey) != 4):
            return True

        else:
            return False

    def singularities(self):
        """Returns all the singularity indices in the quad mesh.

        Returns
        -------
        list
            The list of vertex indices that are quad mesh singularities.

        """
        return [vkey for vkey in self.vertices() if self.is_vertex_singular(vkey)]

    def vertex_index(self, vkey):
        """Compute vertex index.

        Parameters
        ----------
        vkey : int
            The vertex key.

        Returns
        -------
        int
            Vertex index.

        """

        if self.vertex_degree(vkey) == 0:
            return 0

        regular_valency = 4 if not self.is_vertex_on_boundary(vkey) else 3

        return (regular_valency - self.vertex_degree(vkey)) / 4

    # --------------------------------------------------------------------------
    # polyedges
    # --------------------------------------------------------------------------

    def collect_polyedge(self, u0, v0):
        """Collect all the edges in the polyedge of the input edge.

        Parameters
        ----------
        u : int
            The identifier of the edge start.
        v : int
            The identifier of the edge end.

        Returns
        -------
        polyedge : list
            The list of the vertices in polyedge.
        """

        polyedge = [u0, v0]

        while len(polyedge) <= self.number_of_vertices():

            # end if closed loop
            if polyedge[0] == polyedge[-1]:
                break

            # get next vertex accros four-valent vertex
            w = self.vertex_opposite_vertex(*polyedge[-2:])

            # flip if end of first extremity
            if w is None:
                polyedge = list(reversed(polyedge))
                # stop if end of second extremity
                w = self.vertex_opposite_vertex(*polyedge[-2:])
                if w is None:
                    break

            # add next vertex
            polyedge.append(w)

        return polyedge

    def collect_polyedges(self):
        """Collect the polyedges accross four-valent vertices between boundaries and/or singularities and store it in the mesh data attributes.

        Parameters
        ----------

        Returns
        -------
        polyedges : list
            List of quad polyedges as list of vertices.

        """

        edges = list(self.edges())

        nb_polyedges = -1
        while len(edges) > 0:
            nb_polyedges += 1

            # collect new polyedge
            u0, v0 = edges.pop()
            polyedge = self.collect_polyedge(u0, v0)
            self.attributes['polyedges'].update({nb_polyedges: polyedge})

            # remove collected edges
            for u, v in pairwise(polyedge):
                if (u, v) in edges:
                    edges.remove((u, v))
                elif (v, u) in edges:
                    edges.remove((v, u))

        return self.polyedges(data=True)

    def is_polyedge_closed(self, pkey):
        """Output whether a polyedge is closed.

        Parameters
        ----------
        pkey : hashable
            A strip key.

        Returns
        -------
        bool
            True if the polyedge is closed. False otherwise.
        """

        return self.attributes['polyedges'][pkey][0] == self.attributes['polyedges'][pkey][-1]

    def singularity_polyedges(self):
        """Collect the polyedges connected to singularities.

        Returns
        -------
        list
            The polyedges connected to singularities.

        """

        # keep only polyedges connected to singularities or along the boundary
        polyedges = [polyedge for key, polyedge in self.polyedges(data=True) if self.is_vertex_singular(
            polyedge[0]) or self.is_vertex_singular(polyedge[-1]) or self.is_edge_on_boundary(polyedge[0], polyedge[1])]

        # get intersections between polyedges for split
        vertices = [vkey for polyedge in polyedges for vkey in set(polyedge)]
        split_vertices = [vkey for vkey in self.vertices() if vertices.count(vkey) > 1]

        # split singularity polyedges
        return [split_polyedge for polyedge in polyedges for split_polyedge in list_split(polyedge, [polyedge.index(vkey) for vkey in split_vertices if vkey in polyedge])]

    def singularity_polyedge_decomposition(self):
        """Returns a quad patch decomposition of the mesh based on the singularity polyedges, including boundaries and additionnal splits on the boundaries.

        Returns
        -------
        list
            The polyedges forming the decomposition.

        """
        if self.attributes['polyedges'] == {}:
            self.collect_polyedges()

        polyedges = [polyedge for key, polyedge in self.polyedges(data=True) if (self.is_vertex_singular(
            polyedge[0]) or self.is_vertex_singular(polyedge[-1])) and not self.is_edge_on_boundary(polyedge[0], polyedge[1])]

        # split boundaries
        all_splits = list(set([vkey for polyedge in polyedges for vkey in polyedge] + self.singularities()))

        for boundary in self.boundaries():
            splits = [vkey for vkey in boundary if vkey in all_splits]
            new_splits = []

            if len(splits) == 0:
                new_splits += [vkey for vkey in list(itemgetter(0, int(floor(len(boundary) / 3)), int(floor(len(boundary) * 2 / 3)))(boundary))]

            elif len(splits) == 1:
                i = boundary.index(splits[0])
                new_splits += list(itemgetter(i - int(floor(len(boundary) * 2 / 3)), i - int(floor(len(boundary) / 3)))(boundary))

            elif len(splits) == 2:
                one, two = list_split(boundary + boundary[:1], [boundary.index(vkey) for vkey in splits])
                half = one if len(one) > len(two) else two
                new_splits.append(half[int(floor(len(half) / 2))])

            for vkey in new_splits:
                for nbr in self.vertex_neighbors(vkey):
                    if not self.is_edge_on_boundary(vkey, nbr):
                        new_polyedge = self.collect_polyedge(vkey, nbr)
                        polyedges.append(new_polyedge)
                        all_splits = list(set(all_splits + new_polyedge))
                        break

        # add boundaries
        polyedges += [polyedge for key, polyedge in self.polyedges(data=True) if self.is_edge_on_boundary(polyedge[0], polyedge[1])]

        # get intersections between polyedges for split
        vertices = [vkey for polyedge in polyedges for vkey in set(polyedge)]
        split_vertices = [vkey for vkey in self.vertices() if vertices.count(vkey) > 1]

        # split singularity polyedges
        return [
            split_polyedge for polyedge in polyedges
            for split_polyedge in list_split(polyedge, [polyedge.index(vkey) for vkey in split_vertices if vkey in polyedge])]

    # --------------------------------------------------------------------------
    # polylines
    # --------------------------------------------------------------------------

    def polyedge_graph(self):
        """Compute the vertices and edges of the graph representing the polyedge connectivity,
        where each graph vertex is a mesh polyedge and each graph edge a non-compas_singular mesh vertex representing the crossing of two polyedges.
        Polyedges connected by their extremities, which are singularities, do not count as overlapping.
        Potentially includes loop edges (u, u) or multiple arallel edges (u, v) and/or (v, u).

        Returns
        -------
        tuple
            A tuple of two objects, the dictionary of mesh polyedge indices pointing to their centroid coordinates, and the list of edges between graph vertices.
        """

        vertices = {key: centroid_points([self.vertex_coordinates(vkey) for vkey in polyedge]) for key, polyedge in self.polyedges(data=True)}
        edges = []
        for key, polyedge in self.polyedges(data=True):
            for vkey in polyedge:
                if not self.is_vertex_singular(vkey):
                    for key_2, polyedge_2 in self.polyedges(data=True):
                        if vkey in polyedge_2:
                            edges.append((key, key_2))
                            break
        return vertices, edges

    # --------------------------------------------------------------------------
    # polylines
    # --------------------------------------------------------------------------

    def polylines(self):
        """Return the polylines of the quad mesh.

        Returns
        -------
        list
            The polylines.
        """

        return [[self.vertex_coordinates(vkey) for vkey in polyedge] for key, polyedge in self.polyedges(data=True)]

    def singularity_polylines(self):
        """Return the polylines connected to singularities.

        Returns
        -------
        list
            The polylines connected to singularities.

        """
        return [[self.vertex_coordinates(vkey) for vkey in polyedge] for polyedge in self.singularity_polyedges()]

    def singularity_polyline_decomposition(self):
        """Return the polylines forming a quad patch decomposition of the mesh.

        Returns
        -------
        list
            The polylines connected to singularities.

        """
        return [[self.vertex_coordinates(vkey) for vkey in polyedge] for polyedge in self.singularity_polyedge_decomposition()]

    # --------------------------------------------------------------------------
    # strips
    # --------------------------------------------------------------------------

    def number_of_strips(self):
        """Count the number of strips in the mesh."""
        return len(list(self.strips()))

    def collect_strip(self, u0, v0):
        """Returns all the edges in the strip of the input edge.

        Parameters
        ----------
        u : int
            The identifier of the edge start.
        v : int
            The identifier of the edge end.

        Returns
        -------
        strip : list
            The list of the edges in strip.
        """

        if self.halfedge[u0][v0] is None:
            u0, v0 = v0, u0

        edges = [(u0, v0)]

        count = self.number_of_edges()
        while count > 0:
            count -= 1

            u, v = edges[-1]
            w, x = self.face_opposite_edge(u, v)

            if (x, w) == edges[0]:
                break

            edges.append((x, w))

            if w not in self.halfedge[x] or self.halfedge[x][w] is None:
                edges = [(v, u) for u, v in reversed(edges)]
                u, v = edges[-1]
                if v not in self.halfedge[u] or self.halfedge[u][v] is None:
                    break

        return edges

    def collect_strips(self):
        """Collect the strip data and store it in the mesh data attributes.

        Returns
        -------
        strips : dict
            The strip data.
        """

        edges = [(u, v) if self.halfedge[u][v] is not None else (v, u) for u, v in self.edges()]

        nb_strip = -1
        while len(edges) > 0:
            nb_strip += 1

            u0, v0 = edges.pop()
            strip_edges = self.collect_strip(u0, v0)
            self.attributes['strips'].update({nb_strip: strip_edges})
            for u, v in strip_edges:
                if (u, v) in edges:
                    edges.remove((u, v))
                elif (v, u) in edges:
                    edges.remove((v, u))

        return self.strips(data=True)

    def is_strip_closed(self, skey):
        """Output whether a strip is closed.

        Parameters
        ----------
        skey : hashable
            A strip key.

        Returns
        -------
        bool
            True if the strip is closed. False otherwise.
        """

        return not self.is_edge_on_boundary(*self.strip_edges(skey)[0])

    def strip_edges(self, skey):
        """Return the edges of a strip.

        Parameters
        ----------
        skey : hashable
            A strip key.
        Returns
        -------
        list
            The edges of the strip.

        """

        return self.attributes['strips'][skey]

    def edge_strip(self, edge):
        """Return the strip of an edge.

        Parameters
        ----------
        edge : tuple
            An edge as two vertex keys.

        Returns
        -------
        strip
            The strip of the edge.
        """

        for skey, edges in self.strips(data=True):
            if edge in edges or tuple(reversed(edge)) in edges:
                return skey

    def strip_faces(self, skey):
        """Return the faces of a strip.

        Parameters
        ----------
        skey : hashable
            A strip key.

        Returns
        -------
        list
            The faces of the strip.

        """

        return [self.halfedge[u][v] for u, v in self.strip_edges(skey) if self.halfedge[u][v] is not None]

    def face_strips(self, fkey):
        """Return the two strips of a face.

        Parameters
        ----------
        fkey : hashable

        Returns
        -------
        list
            The two strips of the face.
        """

        return [self.edge_strip((u, v)) for u, v in list(self.face_halfedges(fkey))[:2]]

    # --------------------------------------------------------------------------
    # strip data operations
    # --------------------------------------------------------------------------

    def substitute_vertex_in_strips(self, old_vkey, new_vkey, strips=None):
        """Substitute a vertex by another one.

        Parameters
        ----------
        old_vkey : hashable
            The old vertex key.
        new_vkey : hashable
            The new vertex key.
        strips : list
            List of specific strip keys. Per default None, i.e. all.

        """

        if strips is None:
            strips = list(self.strips())
        self.attributes['strips'].update({
            skey: [tuple([new_vkey if vkey == old_vkey else vkey for vkey in list(edge)]) for edge in self.strip_edges(skey)] for skey in strips
        })

    def delete_face_in_strips(self, fkey):
        """Delete face in strips.

        Parameters
        ----------
        old_vkey : hashable
            The old vertex key.
        new_vkey : hashable
            The new vertex key.

        """

        self.attributes['strips'] = {skey: [(u, v) for u, v in self.strip_edges(skey) if self.halfedge[u][v] != fkey] for skey in self.strips()}

    # --------------------------------------------------------------------------
    # strip graph
    # --------------------------------------------------------------------------

    def strip_graph(self):
        """Compute the vertices and edges of the graph representing the strip connectivity,
        where each graph vertex is a mesh strip and each graph edge a mesh face representing the crossing of two strips.
        Potentially includes loop edges (u, u) or multiple arallel edges (u, v) and/or (v, u).

        Returns
        -------
        tuple
            A tuple of two objects, the dictionary of mesh strip keys pointing to graph vertex coordinates,
            and the list of edges between graph vertices.
        """

        vertices = {skey: centroid_points(self.strip_edge_midpoint_polyline(skey) if not self.is_strip_closed(skey)
                                          else self.strip_edge_midpoint_polyline(skey)[:-1]) for skey in self.strips()}
        edges = [tuple(self.face_strips(fkey)) for fkey in self.faces()]
        return vertices, edges

    # --------------------------------------------------------------------------
    # strip polyedges
    # --------------------------------------------------------------------------

    def strip_side_polyedges(self, skey):
        """Return the two side polyedges of a strip.

        Parameters
        ----------
        skey : hashable
            A strip key.

        Returns
        -------
        tuple
            The pair of polyedges on the side of the strip.
        """

        strip_edges = self.strip_edges(skey)

        starts = [edge[0] for edge in strip_edges]
        ends = [edge[1] for edge in strip_edges]

        if self.is_strip_closed(skey):
            starts += starts[:1]
            ends += ends[:1]

        return (starts, ends)

    # --------------------------------------------------------------------------
    # strip polylines
    # --------------------------------------------------------------------------

    def strip_edge_midpoint_polyline(self, skey):
        """Return the strip polyline connecting edge midpoints.

        Parameters
        ----------
        skey : hashable
            A strip key.

        Returns
        -------
        list
            The edge midpoint polyline.
        """

        polyline = [self.edge_midpoint(u, v) for u, v in self.strip_edges(skey)]

        if self.is_strip_closed(skey):
            return polyline + polyline[: 1]

        else:
            return polyline

    def strip_face_centroid_polyline(self, skey):
        """Return the strip polyline connecting face centroids.

        Parameters
        ----------
        skey : hashable
            A strip key.

        Returns
        -------
        list
            The face centroid polyline.
        """

        polyline = [self.face_centroid(fkey) for fkey in self.strip_faces(skey)]

        if self.is_strip_closed(skey):
            return polyline + polyline[: 1]

        else:
            return polyline

    def strip_side_polylines(self, skey):
        """Return the two side polylines of a strip.

        Parameters
        ----------
        skey : hashable
            A strip key.

        Returns
        -------
        tuple
            The pair of polylines on the side of the strip.
        """

        starts, ends = self.strip_side_polyedges(skey)
        return ([self.vertex_coordinates(vkey) for vkey in starts], [self.vertex_coordinates(vkey) for vkey in ends])


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':
    pass

    # import compas
    # from compas_plotters.meshplotter import MeshPlotter

    # # mesh = QuadMesh.from_obj(compas.get('faces.obj'))
    # # mesh = QuadMesh.from_json('/Users/Robin/Desktop/json/debug.json')

    # # mesh.collect_strips()
    # # mesh.collect_polyedges()

    # # print(mesh.singularities())
    # # print(len(list(mesh.strips())))
    # # print(len(list(mesh.polyedges())))

    # # print(len(mesh.singularity_polyedge_decomposition()))

    # # print(mesh.strip_graph())
    # # print(mesh.polyedge_graph())

    # #plotter = MeshPlotter(mesh, figsize=(20, 20))
    # #plotter.draw_vertices(radius=0.4, text='key')
    # # plotter.draw_edges()
    # # plotter.draw_faces()
    # # plotter.show()
