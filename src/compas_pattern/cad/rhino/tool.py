from math import ceil
from compas.utilities import average
from compas.utilities import standard_deviation

from compas_pattern.datastructures.mesh_quad_pseudo_coarse.mesh_quad_pseudo_coarse import CoarsePseudoQuadMesh
from compas_pattern.datastructures.mesh_quad_pseudo.mesh_quad_pseudo import PseudoQuadMesh

from compas.geometry import Polyline

from compas_rhino.geometry import RhinoMesh
from compas_pattern.cad.rhino.objects.surface import RhinoSurface
from compas_pattern.cad.rhino.objects.curve import RhinoCurve
from compas_rhino.geometry import RhinoPoint

from compas_pattern.algorithms.decomposition.algorithm import surface_decomposition

from compas_pattern.datastructures.mesh_quad.grammar_pattern import add_strip
from compas_pattern.datastructures.mesh_quad.grammar_pattern import delete_strips
from compas_pattern.datastructures.mesh_quad.grammar_pattern import split_strip
from compas_pattern.datastructures.mesh_quad.grammar_pattern import boundary_strip_preserve

from compas.topology import *

from compas_pattern.algorithms.relaxation.relaxation import constrained_smoothing
from compas_pattern.algorithms.relaxation.constraints import automated_smoothing_surface_constraints
from compas_pattern.algorithms.relaxation.constraints import automated_smoothing_constraints
from compas_pattern.algorithms.relaxation.constraints import customized_smoothing_constraints
from compas_pattern.algorithms.relaxation.constraints import display_smoothing_constraints

import compas_rhino.artists as rhino_artist
import compas_rhino.helpers as rhino_helper

from compas_pattern.cad.rhino.artist import select_mesh_strip
from compas_pattern.cad.rhino.artist import select_mesh_strips
from compas_pattern.cad.rhino.artist import select_mesh_polyedge


from compas_pattern.cad.rhino.draw import draw_mesh

import compas

try:
    import rhinoscriptsyntax as rs

except ImportError:
    compas.raise_if_ironpython()

__author__ = ['Robin Oval']
__copyright__ = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__ = 'MIT License'
__email__ = 'oval@arch.ethz.ch'


__all__ = [
    'explore_pattern',
    'editing_topology',
    'editing_density'
    'editing_symmetry',
    'editing_geometry',
    'editing_geometry_moving',
    'editing_geometry_smoothing',
    'save_design',
    'evaluate_pattern'
]


def singular():
    """Explore a pattern, its topology (singularities, densities and symmetries) and its geoemtry (via smoothing).

    """

    layer = rs.CurrentLayer()

    pattern_from = rs.GetString('start pattern from?', strings=[
                                'coarse_pseudo_quad_mesh', 'pseudo_quad_mesh', 'surface_and_features'])

    if pattern_from == 'coarse_pseudo_quad_mesh':
        guid = rs.GetObject('get coarse quad mesh', filter=32)
        coarse_pseudo_quad_mesh = CoarsePseudoQuadMesh.from_vertices_and_faces(
            *RhinoMesh.from_guid(guid).get_vertices_and_faces())
        coarse_pseudo_quad_mesh.init_strip_density()
        coarse_pseudo_quad_mesh.quad_mesh = coarse_pseudo_quad_mesh.copy()
        coarse_pseudo_quad_mesh.polygonal_mesh = coarse_pseudo_quad_mesh.copy()
    elif pattern_from == 'pseudo_quad_mesh':
        guid = rs.GetObject('get quad mesh', filter=32)
        coarse_pseudo_quad_mesh = CoarsePseudoQuadMesh.from_quad_mesh(PseudoQuadMesh.from_vertices_and_faces(
            *RhinoMesh.from_guid(guid).get_vertices_and_faces()))
    elif pattern_from == 'surface_and_features':
        srf_guid = rs.GetObject('get surface', filter=8)
        crv_guids = rs.GetObjects('get optional curve features', filter=4)
        if crv_guids is None:
            crv_guids = []
        pt_guids = rs.GetObjects('get optional point features', filter=1)
        if pt_guids is None:
            pt_guids = []
        coarse_pseudo_quad_mesh = surface_decomposition(srf_guid, rs.GetReal('precision', number=1.), crv_guids=crv_guids, pt_guids=pt_guids, output_skeleton=False)[0]
        coarse_pseudo_quad_mesh.init_strip_density()
        coarse_pseudo_quad_mesh.quad_mesh = coarse_pseudo_quad_mesh.copy()
        coarse_pseudo_quad_mesh.polygonal_mesh = coarse_pseudo_quad_mesh.copy()
        guid = draw_mesh(coarse_pseudo_quad_mesh)
    else:
        return 0

    while True:

        #edit = rs.GetString('edit pattern?', strings = ['topology', 'density', 'symmetry', 'geometry', 'evaluate', 'exit'])
        edit = rs.GetString('edit pattern?', strings=[
                            'topology', 'density', 'symmetry', 'geometry', 'save', 'exit'])

        if type(guid) == list:
            rs.DeleteObjects(guid)
        else:
            rs.DeleteObject(guid)

        if edit is None or edit == 'exit':
            rs.EnableRedraw(False)
            return draw_mesh(coarse_pseudo_quad_mesh.polygonal_mesh)

        if edit == 'topology':
            editing_topology(coarse_pseudo_quad_mesh)
            coarse_pseudo_quad_mesh.densification()
            coarse_pseudo_quad_mesh.polygonal_mesh = coarse_pseudo_quad_mesh.quad_mesh.copy()

        elif edit == 'density':
            editing_density(coarse_pseudo_quad_mesh)
            coarse_pseudo_quad_mesh.polygonal_mesh = coarse_pseudo_quad_mesh.quad_mesh.copy()

        elif edit == 'symmetry':
            editing_symmetry(coarse_pseudo_quad_mesh)

        elif edit == 'geometry':
            editing_geometry(coarse_pseudo_quad_mesh)

        rs.EnableRedraw(False)
        guid = draw_mesh(coarse_pseudo_quad_mesh.polygonal_mesh)
        rs.EnableRedraw(True)

        if edit == 'save':
            save_design(coarse_pseudo_quad_mesh, layer)

        if edit == 'evaluate':
            evaluate_pattern(coarse_pseudo_quad_mesh.polygonal_mesh)


def editing_topology(coarse_pseudo_quad_mesh):
    """Edit the topology of a pattern, i.e. its singularities, via its strips.

    Parameters
    ----------
    coarse_pseudo_quad_mesh : CoarsePseudoQuadMesh
            The pattern to edit.

    """

    while True:

        # update drawing
        rs.EnableRedraw(False)
        guid = draw_mesh(coarse_pseudo_quad_mesh)
        rs.EnableRedraw(True)

        # choose operation
        operation = rs.GetString('edit strip topology?', strings=[
                                 'add', 'delete', 'split', 'exit'])

        # stop if asked
        if operation is None or operation == 'exit':
            rs.DeleteObject(guid)
            break

        # apply operation
        if operation == 'add':
            skey = add_strip(coarse_pseudo_quad_mesh,
                             select_mesh_polyedge(coarse_pseudo_quad_mesh))[0]
            coarse_pseudo_quad_mesh.set_strip_density(skey, 1)

        elif operation == 'delete':
            skeys = set(select_mesh_strips(coarse_pseudo_quad_mesh))
            skey_to_skeys = delete_strips(
                coarse_pseudo_quad_mesh, skeys, preserve_boundaries=True)
            if skey_to_skeys is not None:
                for skey_0, skeys in skey_to_skeys.items():
                    d = int(
                        ceil(float(coarse_pseudo_quad_mesh.get_strip_density(skey_0)) / 2.))
                    coarse_pseudo_quad_mesh.set_strips_density(d, skeys)

        elif operation == 'split':
            skey = select_mesh_strip(coarse_pseudo_quad_mesh)
            n = rs.GetInteger('number of splits', number=2, minimum=2)
            skeys = split_strip(coarse_pseudo_quad_mesh, skey, n=n)
            # update data
            d = int(ceil(float(coarse_pseudo_quad_mesh.get_strip_density(skey)) / float(n)))
            coarse_pseudo_quad_mesh.set_strips_density(d, skeys)

        # delete drawing
        rs.DeleteObject(guid)


def editing_density(coarse_pseudo_quad_mesh):
    """Edit the density of a pattern via its strip densities.

    Parameters
    ----------
    coarse_pseudo_quad_mesh : CoarsePseudoQuadMesh
            The pattern to edit.

    """

    while True:

        # update drawing
        rs.EnableRedraw(False)
        guid = draw_mesh(coarse_pseudo_quad_mesh.quad_mesh)
        rs.EnableRedraw(True)

        # choose operation
        operation = rs.GetString('edit strip density?', strings=[
                                 'global_density_value', 'global_subdivision_target_length', 'strip_density_value', 'strip_subdivision_target_length', 'global_uniform_target_number_faces', 'exit'])

        # stop if asked
        if operation is None or operation == 'exit':
            rs.DeleteObjects(guid)
            break

        # get operation parameters
        if 'strip' in operation:
            skey = select_mesh_strip(coarse_pseudo_quad_mesh, show_density=True)

        if 'value' in operation:
            d = rs.GetInteger('density value', number=3, minimum=1)
        elif 'length' in operation:
            t = rs.GetReal('density target', number=1.)
        elif 'faces' in operation:
            nb_faces = rs.GetInteger('density value', number=100, minimum=1)

        # apply operation
        if operation == 'strip_density_value':
            coarse_pseudo_quad_mesh.set_strip_density(skey, d)

        elif operation == 'global_density_value':
            coarse_pseudo_quad_mesh.set_strips_density(d)

        elif operation == 'strip_subdivision_target_length':
            coarse_pseudo_quad_mesh.set_strip_density_target(skey, t)

        elif operation == 'global_subdivision_target_length':
            coarse_pseudo_quad_mesh.set_strips_density_target(t)

        elif operation == 'global_uniform_target_number_faces':

            coarse_pseudo_quad_mesh.set_strips_density_equal_face_target(nb_faces)

        # update data
        coarse_pseudo_quad_mesh.densification()

        # delete drawing
        rs.DeleteObjects(guid)


def editing_symmetry(coarse_pseudo_quad_mesh):
    """Edit the symmetry of a pattern via Conway operators.

    Parameters
    ----------
    coarse_pseudo_quad_mesh : CoarsePseudoQuadMesh
            The pattern to edit.

    """

    conway_operators = {
        'conway_seed',
        'conway_dual',
        'conway_join',
        'conway_ambo',
        'conway_kis',
        'conway_needle',
        'conway_zip',
        'conway_truncate',
        'conway_ortho',
        'conway_expand',
        'conway_gyro',
        'conway_snub',
        'conway_meta',
        'conway_bevel'
    }

    conway = {operator[7:]: operator for operator in conway_operators}

    while True:

        rs.EnableRedraw(False)
        guid = draw_mesh(coarse_pseudo_quad_mesh.polygonal_mesh)
        rs.EnableRedraw(True)

        operator = rs.GetString(
            'Conway operator?', strings=conway.keys() + ['exit'])

        if operator is None or operator == 'exit':
            if type(guid) == list:
                rs.DeleteObjects(guid)
            else:
                rs.DeleteObject(guid)
            return coarse_pseudo_quad_mesh.polygonal_mesh

        elif operator == 'seed':
            coarse_pseudo_quad_mesh.polygonal_mesh = coarse_pseudo_quad_mesh.quad_mesh.copy()

        elif operator in conway and conway[operator] in globals() and str(conway[operator])[: 6] == 'conway':
            coarse_pseudo_quad_mesh.polygonal_mesh = globals()[conway[operator]](
                coarse_pseudo_quad_mesh.polygonal_mesh)

        if type(guid) == list:
            rs.DeleteObjects(guid)
        else:
            rs.DeleteObject(guid)


def editing_geometry(coarse_pseudo_quad_mesh):

    geom_operation = rs.GetString(
        'geometrical modification?', strings=['moving', 'smoothing'])

    if geom_operation == 'moving':
        editing_geometry_moving(coarse_pseudo_quad_mesh)
    elif geom_operation == 'smoothing':
        editing_geometry_smoothing(coarse_pseudo_quad_mesh)


def editing_geometry_moving(coarse_pseudo_quad_mesh):
    """Edit the geometry of a pattern with moving.

    Parameters
    ----------
    coarse_pseudo_quad_mesh : CoarsePseudoQuadMesh
            The pattern to edit.

    """

    mesh_to_modify = rs.GetString('mesh to modify?', strings=[
                                  'coarse_pseudo_quad_mesh', 'pseudo_quad_mesh', 'polygonal_mesh'])
    if mesh_to_modify == 'coarse_pseudo_quad_mesh':
        mesh = coarse_pseudo_quad_mesh
    elif mesh_to_modify == 'pseudo_quad_mesh':
        mesh = coarse_pseudo_quad_mesh.quad_mesh
    elif mesh_to_modify == 'polygonal_mesh':
        mesh = coarse_pseudo_quad_mesh.polygonal_mesh
    else:
        return 0

    while True:

        rs.EnableRedraw(False)
        guid = draw_mesh(mesh)
        rs.EnableRedraw(True)

        artist = rhino_artist.MeshArtist(mesh, layer='mesh_artist')
        artist.clear_layer()
        artist.draw_vertexlabels(text={key: str(key)
                                       for key in mesh.vertices()})
        artist.redraw()
        vkeys = rhino_helper.mesh_select_vertices(
            mesh, message='vertices to move')
        artist.clear_layer()
        artist.redraw()
        rs.DeleteLayer('mesh_artist')

        if vkeys == []:
            rs.DeleteObject(guid)
            break

        rhino_helper.mesh_move_vertices(mesh, vkeys)
        rs.DeleteObject(guid)

    if mesh_to_modify == 'pseudo_quad_mesh':
        coarse_pseudo_quad_mesh.polygonal_mesh = mesh

def editing_geometry_smoothing(coarse_pseudo_quad_mesh):
    """Edit the geometry of a pattern with smoothing.

    Parameters
    ----------
    coarse_pseudo_quad_mesh : CoarsePseudoQuadMesh
            The pattern to edit.

    """

    mesh_to_smooth = rs.GetString('mesh to smooth?', strings=[
                                  'coarse_pseudo_quad_mesh', 'pseudo_quad_mesh', 'polygonal_mesh'])
    if mesh_to_smooth == 'coarse_pseudo_quad_mesh':
        mesh = coarse_pseudo_quad_mesh
    elif mesh_to_smooth == 'pseudo_quad_mesh':
        mesh = coarse_pseudo_quad_mesh.quad_mesh
    elif mesh_to_smooth == 'polygonal_mesh':
        mesh = coarse_pseudo_quad_mesh.polygonal_mesh
    else:
        return 0

    settings = {'iterations': 50, 'damping': .5, 'constraints': {}}

    while True:

        rs.EnableRedraw(False)
        guid = draw_mesh(mesh)
        rs.EnableRedraw(True)

        operation = rs.GetString('edit smoothing settings?', strings=[
                                 'smooth', 'iterations', 'damping', 'constraints', 'exit'])

        if operation is None or operation == 'exit':
            if type(guid) == list:
                rs.DeleteObjects(guid)
            else:
                rs.DeleteObject(guid)
            break

        elif operation == 'iterations':
            settings[operation] = rs.GetInteger(
                'iterations', number=settings[operation], minimum=0)

        elif operation == 'damping':
            settings[operation] = rs.GetReal('damping', number=settings[
                                             operation], minimum=0., maximum=1.)

        elif operation == 'constraints':
            count = 100
            while count:
                count -= 1
                guids = display_smoothing_constraints(
                    mesh, settings[operation])
                constraint_type = rs.GetString('type of constraints?', strings=[
                                               'automated_from_surface', 'automated_from_objects', 'customised', 'reset', 'exit'])
                rs.DeleteObjects(guids)
                if constraint_type == 'automated_from_surface':
                    settings[operation] = automated_smoothing_surface_constraints(
                        mesh, RhinoSurface(rs.GetObject('surface constraints', filter=8)))
                elif constraint_type == 'automated_from_objects':
                    object_constraints = rs.GetObjects('object constraints')
                    point_constraints = [
                        obj for obj in object_constraints if rs.ObjectType(obj) == 1]
                    curve_constraints = [
                        obj for obj in object_constraints if rs.ObjectType(obj) == 4]
                    surface_constraint = [
                        obj for obj in object_constraints if rs.ObjectType(obj) == 8]
                    if len(surface_constraint) > 1:
                        print 'More than one surface constraint! Only the first one is taken into account.'
                    if len(surface_constraint) == 0:
                        surface_constraint = None
                    else:
                        surface_constraint = surface_constraint[0]
                    settings[operation] = automated_smoothing_constraints(
                        mesh, point_constraints, curve_constraints, surface_constraint)
                elif constraint_type == 'customised':
                    settings[operation] = customized_smoothing_constraints(mesh, settings[
                                                                           operation])
                elif constraint_type == 'reset':
                    settings[operation] = {}
                else:
                    break

        elif operation == 'smooth':
            constrained_smoothing(mesh, kmax=settings['iterations'], damping=settings[
                                  'damping'], constraints=settings['constraints'], algorithm='area')

        if type(guid) == list:
            rs.DeleteObjects(guid)
        else:
            rs.DeleteObject(guid)

    if mesh_to_smooth == 'pseudo_quad_mesh':
        coarse_pseudo_quad_mesh.polygonal_mesh = mesh

def save_design(coarse_pseudo_quad_mesh, layer):
    """Save one of the meshes based on the coarse quad mesh.

    Parameters
    ----------
    mesh : CoarsePseudoQuadMesh
            The coarse quad mesh from which to save data.

    """

    mesh_to_save = rs.GetString('mesh to save?', strings=[
                                  'coarse_pseudo_quad_mesh', 'pseudo_quad_mesh', 'polygonal_mesh'])
    
    guid = None
    if mesh_to_save == 'coarse_pseudo_quad_mesh':
        guid = draw_mesh(coarse_pseudo_quad_mesh)
    elif mesh_to_save == 'pseudo_quad_mesh':
        guid = draw_mesh(coarse_pseudo_quad_mesh.quad_mesh)
    elif mesh_to_save == 'polygonal_mesh':
        guid = draw_mesh(coarse_pseudo_quad_mesh.polygonal_mesh)
    
    if guid is not None:
        layer = rs.GetLayer(layer=layer)
        rs.ObjectLayer(guid, layer)


def evaluate_pattern(mesh):
    """Evaluate the properties of a mesh.

    Parameters
    ----------
    mesh : Mesh
            The mesh to evaluate.

    """

    while True:

        metric_type = rs.GetString('evaluate pattern property?', strings=[
                                   'topology', 'geometry', 'exit'])

        if metric_type is None or metric_type == 'exit':
            break

        if metric_type == 'topology':
            metric = rs.GetString('evaluate topological property?', strings=[
                                  'euler', 'genus', 'boundaries'])
            if metric == 'euler':
                print 'euler: ', mesh.euler()
            elif metric == 'genus':
                print 'genus: ', mesh.genus()
            elif metric == 'boundaries':
                print 'boundaries: ', len(mesh.boundaries())

        elif metric_type == 'geometry':
            metric = rs.GetString('evaluate geometrical property?', strings=[
                                  'edge_length', 'face_area', 'face_aspect_ratio', 'face_skewness', 'face_curvature', 'vertex_curvature'])

            aspect = rs.GetString('evaluate geometrical property?', strings=[
                                  'all', 'min', 'max', 'average', 'standard_deviation', 'specific'])

            if metric == 'edge_length':
                if aspect == 'specific':
                    guids = rhino_helper.mesh_draw_edges(mesh)
                    edges = rhino_helper.mesh_select_edges(mesh)
                    rs.DeleteObjects(guids)
                    print[mesh.edge_length(*edge) for edge in edges]
                else:
                    edge_lengths = [mesh.edge_length(
                        *edge) for edge in mesh.edges()]
                    if aspect == 'all':
                        print edge_lengths
                    elif aspect == 'min':
                        print min(edge_lengths)
                    elif aspect == 'max':
                        print max(edge_lengths)
                    elif aspect == 'average':
                        print average(edge_lengths)
                    elif aspect == 'standard_deviation':
                        print standard_deviation(edge_lengths)

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas
