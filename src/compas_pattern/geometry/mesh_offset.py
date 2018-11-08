from compas_pattern.datastructures.mesh import Mesh

from compas.geometry import add_vectors
from compas.geometry import scale_vector

from compas.topology import mesh_flip_cycles
from compas_pattern.topology.joining_welding import join_meshes

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [
    'mesh_offset',
    'mesh_thicken',
]

def mesh_offset(mesh, offset = 1.):
    """Offset a mesh.

    Parameters
    ----------
    mesh : Mesh
        A Mesh to offset.
    offset : real
        The offset distance.


    Returns
    -------
    Mesh
        The offset mesh.

    """

    # new coordinates of vertex keys
    vertex_map = {vkey: (i, [0,0,0]) if len(mesh.vertex_neighbors(vkey)) == 0 else (i, add_vectors(mesh.vertex_coordinates(vkey), scale_vector(mesh.vertex_normal(vkey), offset))) for i, vkey in enumerate(mesh.vertices())}
    
    vertices = [xyz for i, xyz in vertex_map.values()]   
    faces = [[vertex_map[vkey][0] for vkey in mesh.face_vertices(fkey)] for fkey in mesh.faces()] 
    
    return Mesh.from_vertices_and_faces(vertices, faces)

def mesh_thicken(mesh, thickness = 1.):
    """Thicken a mesh.

    Parameters
    ----------
    mesh : Mesh
        A mesh to thicken.
    thickness : real
        The mesh thickness

    Returns
    -------
    thickened_mesh : Mesh
        The thickened mesh.
    """

    # offset in both directions
    mesh_top = mesh_offset(mesh, thickness / 2.)
    mesh_bottom = mesh_offset(mesh, - thickness / 2.)

    # flip bottom part
    mesh_flip_cycles(mesh_bottom)

    # join parts
    thickened_mesh = join_meshes([mesh_top, mesh_bottom])

    # close boundaries
    n = thickened_mesh.number_of_vertices() / 2
    for u, v in list(thickened_mesh.edges_on_boundary()):
        if u < n and v < n:
            thickened_mesh.add_face([u, v, v + n, u + n])

    return thickened_mesh

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas

    mesh = Mesh.from_obj(compas.get('faces.obj'))
