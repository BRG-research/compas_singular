from math import pi
from math import sin

from compas_pattern.datastructures.mesh_quad.coloring import quad_mesh_polyedge_2_coloring
from compas.geometry import scale_vector

__author__ = ['Robin Oval']
__copyright__ = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__ = 'MIT License'
__email__ = 'oval@arch.ethz.ch'

__all__ = [
    'fold',
    'corrugate'
]


def move_vertex(mesh, vkey, vector):
    dx, dy, dz = vector
    attr = mesh.vertex[vkey]
    attr['x'] += dx
    attr['y'] += dy
    attr['z'] += dz


def move_vertices(mesh, moves):
    for vkey, vector in moves.items():
        move_vertex(mesh, vkey, vector)


def quad_mesh_polyedge_direction(quad_mesh, direction):
    polyedges = quad_mesh.polyedges()
    idx_to_color = quad_mesh_polyedge_2_coloring(quad_mesh)
    return [polyedges[idx] for idx, color in idx_to_color.items() if color == direction]


def quad_mesh_polyedge_align(quad_mesh, polyedges_0, polyedges_1):
    # make a stack
    # start with one, get an othrogonal polyedge and align the other
    # cluster per strip before?
    pass


def fold_quad_mesh(quad_mesh, polyedges, amplitude):
    moves = {}
    for polyedge in polyedges:
        for i, vkey in enumerate(polyedge):
            normal = quad_mesh.vertex_normal(vkey)
            eps = (i % 2) * 2 - 1
            factor = eps * amplitude / 2
            moves[vkey] = scale_vector(normal, factor)
    move_vertices(quad_mesh, moves)
    return moves


def corrugate_quad_mesh(quad_mesh, polyedges, amplitude, wavelength):
    moves = {}
    for polyedge in polyedges:
        n = len(polyedge)
        for i, vkey in enumerate(polyedge):
            normal = quad_mesh.vertex_normal(vkey)
            factor = amplitude / 2. * sin(wavelength * float(i) / float(n - 1))
            moves[vkey] = scale_vector(normal, factor)
    move_vertices(quad_mesh, moves)
    return moves


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas
