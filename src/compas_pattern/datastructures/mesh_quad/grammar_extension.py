__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [
]


# def clear_faces(mesh, fkeys, vkeys):
#     # groups of fkeys must be a topological disc
#     # vkeys must be four vertices part of the fkeys boundary

#     vertices = [mesh.vertex_coordinates(vkey) for vkey in mesh.vertices()]
#     face_vertices = [mesh.face_vertices(fkey) for fkey in fkeys]

#     faces_mesh = PseudoQuadMesh.from_vertices_and_faces(vertices, face_vertices)
#     faces_boundary_vertices = mesh.polyedge_boundaries()[0]
#     faces_boundary_vertices = list(reversed(faces_boundary_vertices[:-1]))

#     for fkey in fkeys:
#         mesh.delete_face(fkey)

#     # orientation? reverse boundary vertices?
#     fkey = mesh.add_face(faces_boundary_vertices)

#     new_fkeys = face_propagation(mesh, fkey, vkeys)

#     return new_fkeys


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas
