from math import pi
from math import sin

from compas_pattern.datastructures.mesh_quad.coloring import quad_mesh_polyedge_2_coloring
from compas.geometry import scale_vector
from compas_pattern.datastructures.mesh.operations import mesh_move_vertices_by

__all__ = [
    'fold_quad_mesh',
    'corrugate_quad_mesh'
]


def quad_mesh_polyedge_direction(quad_mesh, direction):
    polyedges = quad_mesh.polyedges()
    idx_to_color = quad_mesh_polyedge_2_coloring(quad_mesh)
    return [polyedges[idx] for idx, color in idx_to_color.items() if color == direction]


def quad_mesh_polyedge_align(quad_mesh, polyedges_0, polyedges_1):
    # make a stack
    # start with one, get an othrogonal polyedge and align the other
    # cluster per strip before?
    #vertex_to_polyedges = {vkey: [] for vkey in quad_mesh.vertices()}
    #for polyedge in polyedges_0 + polyegdges_1:


    pass


def fold_quad_mesh(quad_mesh, polyedges, amplitude):
    moves = {}
    for polyedge in polyedges:
        for i, vkey in enumerate(polyedge):
            normal = quad_mesh.vertex_normal(vkey)
            eps = (i % 2) * 2 - 1
            factor = eps * amplitude / 2
            moves[vkey] = scale_vector(normal, factor)
    mesh_move_vertices_by(quad_mesh, moves)
    return moves


def corrugate_quad_mesh(quad_mesh, polyedges, amplitudes, numbers):
    # amplitudes : list of amplitude of corrugations for each polyedge
    # numbers : list of number of corrugations for each polyedge
    moves = {}
    for polyedge in polyedges:
        n = len(polyedge)
        for i, vkey in enumerate(polyedge):
            normal = quad_mesh.vertex_normal(vkey)
            factor = amplitudes[i] / 2. * sin(2 * pi * numbers[i] * float(i) / float(n - 1))
            moves[vkey] = scale_vector(normal, factor)
    mesh_move_vertices_by(quad_mesh, moves)
    return moves


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas
