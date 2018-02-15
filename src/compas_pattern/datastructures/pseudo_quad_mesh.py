from compas.datastructures.mesh import Mesh

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [

]

class PseudoQuadMesh(Mesh):

    def __init__(self):
        super(PseudoQuadMesh, self).__init__()

    def add_face(self, vertices, fkey=None, attr_dict=None, **kwattr):
        """Add a face to the mesh object. Allow [a, b, c, c] faces.

        Parameters
        ----------
        vertices : list
            A list of vertex keys.
            For every vertex that does not yet exist, a new vertex is created.
        attr_dict : dict, optional
            Face attributes.
        kwattr : dict, optional
            Additional named face attributes.
            Named face attributes overwrite corresponding attributes in the
            attribute dict (``attr_dict``).

        Returns
        -------
        int
            The key of the face.
            The key is an integer, if no key was provided.
        hashable
            The key of the face.
            Any hashable object may be provided as identifier for the face.
            Provided keys are returned unchanged.

        Raises
        ------
        TypeError
            If the provided face key is of an unhashable type.

        Notes
        -----
        If no key is provided for the face, one is generated
        automatically. An automatically generated key is an integer that increments
        the highest integer value of any key used so far by 1.

        If a key with an integer value is provided that is higher than the current
        highest integer key value, then the highest integer value is updated accordingly.

        See Also
        --------
        * :meth:`add_vertex`
        * :meth:`add_edge`

        Examples
        --------
        >>>

        """
        attr = self._compile_fattr(attr_dict, kwattr)

        # remove clean vertices to allow [a, b, c, c] faces
        #self._clean_vertices(vertices)

        if len(vertices) < 3:
            return

        keys = []
        for key in vertices:
            if key not in self.vertex:
                key = self.add_vertex(key)
            keys.append(key)

        fkey = self._get_face_key(fkey)

        self.face[fkey] = keys
        self.facedata[fkey] = attr

        for u, v in self._cycle_keys(keys):
            self.halfedge[u][v] = fkey
            if u not in self.halfedge[v]:
                self.halfedge[v][u] = None

        return fkey

    def delete_face(self, fkey):
        """Delete a face from the mesh object. Valid for [a, b, c, c] faces.

        Parameters
        ----------
        fkey : hashable
            The identifier of the face.

        Examples
        --------
        .. plot::
            :include-source:

            import compas
            from compas.datastructures import Mesh
            from compas.plotters import MeshPlotter

            mesh = Mesh.from_obj(compas.get('faces.obj'))

            mesh.delete_face(12)

            plotter = MeshPlotter(mesh)
            plotter.draw_vertices()
            plotter.draw_faces()
            plotter.show()

        """
        for u, v in self.face_halfedges(fkey):
            self.halfedge[u][v] = None
            if self.halfedge[v][u] is None:
                del self.halfedge[u][v]
                # exception for pseudo quad face
                if u != v:
                    del self.halfedge[v][u]
        del self.face[fkey]

    def to_mesh(self):
        vertices = [self.vertex_coordinates(vkey) for vkey in self.vertices()]
        face_vertices = [self.face_vertices(fkey) for fkey in self.faces()]
        mesh = Mesh.from_vertices_and_faces(vertices, face_vertices)
        return mesh


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas