from compas.datastructures.mesh import Mesh

from compas.utilities import geometric_key

from compas.geometry.algorithms.interpolation import discrete_coons_patch

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [
    'face_propagation',
]

def face_propagation(mesh, fkey, original_vertices):

    face_vertices = mesh.face_vertices(fkey)

    face_vertex_map = {geometric_key(mesh.vertex_coordinates(vkey)): vkey for vkey in face_vertices}
    #print face_vertex_map
    if len(original_vertices) != 4:
        return None

    for vkey in original_vertices:
        if vkey not in face_vertices:
            return None

    a, b, c, d = sorted([face_vertices.index(vkey) for vkey in original_vertices])

    ab = face_vertices[a : b + 1 - len(face_vertices)]
    bc = face_vertices[b : c + 1 - len(face_vertices)]
    cd = face_vertices[c : d + 1 ]#- len(face_vertices)]
    da = face_vertices[d :] + face_vertices[: a + 1 - len(face_vertices)]
    print ab, bc, cd, da

    if len(ab) != len(cd):
        return None
    if len(bc) != len(da):
        return None

    m = len(ab)
    n = len(bc)
    ab = [mesh.vertex_coordinates(vkey) for vkey in ab]
    bc = [mesh.vertex_coordinates(vkey) for vkey in bc]
    dc = list(reversed([mesh.vertex_coordinates(vkey) for vkey in cd]))
    ad = list(reversed([mesh.vertex_coordinates(vkey) for vkey in da]))

    new_vertices, new_face_vertices = discrete_coons_patch(ab, bc, dc, ad)
    
    vertex_remap = []
    for vertex in new_vertices:
        geom_key = geometric_key(vertex)
        if geom_key in face_vertex_map:
            vertex_remap.append(face_vertex_map[geom_key])
        else:
            x, y, z = vertex
            vkey = mesh.add_vertex(attr_dict = {'x': x, 'y': y, 'z': z})
            vertex_remap.append(vkey)

    for face in new_face_vertices:
        mesh.add_face([vertex_remap[vkey] for vkey in face])
    
    mesh.delete_face(fkey)

    return mesh

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas