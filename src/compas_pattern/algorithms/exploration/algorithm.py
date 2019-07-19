from math import floor

import operator
import itertools

from compas_pattern.algorithms.combination.enumeration import enumerate_addition_rules
from compas_pattern.algorithms.combination.enumeration import enumerate_deletion_rules
from compas_pattern.algorithms.combination.combination import apply_rules

from compas_pattern.algorithms.combination.interactivity import select_topology_combinations
from compas_pattern.algorithms.combination.interactivity import draw_topologies_in_spiral
from compas_pattern.algorithms.combination.interactivity import get_addition_rules
from compas_pattern.algorithms.combination.interactivity import get_deletion_rules

from compas_pattern.algorithms.combination.arrange import arrange_in_map

from compas_pattern.cad.rhino.draw import draw_mesh

try:
    import rhinoscriptsyntax as rs
    import scriptcontext as sc

    from Rhino.Geometry import Point3d

    find_object = sc.doc.Objects.Find

except ImportError:
    import compas
    compas.raise_if_ironpython()

__all__ = [
    'adjacent_topologies'
    'combine_adjacent_topologies',
    'interpolate_adjacent_topologies',
    'interactive_combine_adjacent_topologies',
    'interpolate_topologies'
]


def adjacent_topologies(coarse_quad_mesh, include_deletion_rules=True, include_addition_rules=True, kmin=2, kmax=3):

    rules = []

    if include_deletion_rules:
        rules += enumerate_deletion_rules(coarse_quad_mesh)

    if include_addition_rules:
        rules += enumerate_addition_rules(coarse_quad_mesh,
                                          range(kmin, kmax + 1))

    print len(rules), 'rules enumerated'
    topologies = {apply_rules(coarse_quad_mesh, [rule]): [
        rule] for rule in rules}

    return topologies


def combine_adjacent_topologies(coarse_quad_mesh, include_deletion_rules=True, include_addition_rules=True, kmin=2, kmax=3, callback=None, callback_args=None):

    topologies = adjacent_topologies(
        coarse_quad_mesh, include_deletion_rules, include_addition_rules, kmin, kmax)

    combinations = select_topology_combinations(
        topologies, callback, callback_args)
    combined_topologies = {}

    for combination in combinations:
        all_rules = [rule for rules in combination.values() for rule in rules]
        rules_without_duplicates = []
        for rule in all_rules:
            if rule not in rules_without_duplicates:
                rules_without_duplicates.append(rule)
        combined_topologies[apply_rules(
            coarse_quad_mesh, rules_without_duplicates)] = rules_without_duplicates

    return combined_topologies


def interpolate_adjacent_topologies(coarse_quad_mesh, include_deletion_rules=True, include_addition_rules=True, kmin=2, kmax=3, callback=None, callback_args=None):

    combined_topologies = combine_adjacent_topologies(
        coarse_quad_mesh, include_deletion_rules, include_addition_rules, kmin, kmax, callback, callback_args)

    all_rules = list(
        set([rule for rules in combined_topologies.values() for rule in rules]))

    interpolated_topologies = {}

    for k in range(0, len(all_rules) + 1):
        for sub_rules in itertools.combinations(all_rules, k):
            interpolated_topologies.update(
                {apply_rules(coarse_quad_mesh, sub_rules): sub_rules})

    return combined_topologies, interpolated_topologies


def interactive_combine_adjacent_topologies(coarse_quad_mesh, include_deletion_rules=True, include_addition_rules=True, kmin=2, kmax=3, callback=None, callback_args=None):

    def dummy(something, args):
        return something

    if not callback or not callable(callback):
        callback = dummy

    history = [coarse_quad_mesh]

    topologies = adjacent_topologies(
        coarse_quad_mesh, include_deletion_rules, include_addition_rules, kmin, kmax)
    meshes = {mesh: len(rules[0]) for mesh, rules in topologies.items()}
    meshes = [key for key, value in sorted(
        meshes.items(), key=operator.itemgetter(1))]
    rs.EnableRedraw(False)
    guid_to_mesh = draw_topologies_in_spiral(meshes, dummy, callback_args)
    rs.EnableRedraw(True)

    guid_status = {guid: 0 for guid in guid_to_mesh.keys()}

    func_coarse_quad_mesh = coarse_quad_mesh.copy()
    func_coarse_quad_mesh = callback(func_coarse_quad_mesh, callback_args)
    combined_guid = draw_mesh(func_coarse_quad_mesh)

    count = 10
    while count:
        count -= 1
        toggle_guids = rs.GetObjects(
            'select topologies', objects=guid_to_mesh.keys())

        if toggle_guids is None:
            break

        for guid in toggle_guids:
            guid_status[guid] = 1 - guid_status[guid]

        rs.EnableRedraw(False)
        for guid, status in guid_status.items():
            rs.ObjectColor(guid, [200 * (1 - status)] * 3)
        rs.EnableRedraw(True)

        selected_guids = [guid for guid,
                          status in guid_status.items() if status]
        selected_topologies = {guid_to_mesh[guid]: topologies[
            guid_to_mesh[guid]] for guid in selected_guids}

        rules = [rules[0] for rules in selected_topologies.values()]

        rs.EnableRedraw(False)
        combined_mesh = callback(apply_rules(
            coarse_quad_mesh, rules), callback_args)
        history.append(combined_mesh)
        rs.DeleteObject(combined_guid)
        combined_guid = draw_mesh(combined_mesh)
        rs.EnableRedraw(True)

    return history


def interpolate_topologies(coarse_quad_mesh, rules):

    interpolated_topologies = {}

    for k in range(0, len(rules) + 1):
        for sub_rules in itertools.combinations(rules, k):
            interpolated_topologies.update(
                {apply_rules(coarse_quad_mesh, sub_rules): sub_rules})

    return interpolated_topologies


def interpolate_topologies_map(coarse_quad_mesh, combinations):

    all_rules = [rule for combination in combinations for rule in combination]
    print all_rules
    secondary_topologies = {}
    for k in range(0, len(all_rules) + 1):
        for sub_rules in itertools.combinations(all_rules, k):
            is_primary = False
            for combination in combinations:
                if all([rule in combination for rule in sub_rules]):
                    is_primary = True
                    break
            if not is_primary:
            	print sub_rules
                secondary_topologies.update(
                    {apply_rules(coarse_quad_mesh, sub_rules): sub_rules})

    primary_topologies = {apply_rules(coarse_quad_mesh, combination): combination for combination in combinations}
    arrange_in_map(primary_topologies, secondary_topologies)

    return primary_topologies, secondary_topologies


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas
