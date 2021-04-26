from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import time
import itertools

from compas.topology import adjacency_from_edges

from compas_singular.datastructures import QuadMesh
from compas_singular.datastructures import delete_strips
from compas_singular.datastructures import collateral_strip_deletions
from compas_singular.datastructures import total_boundary_deletions
from compas_singular.topology import is_adjacency_two_colorable
from compas_singular.utilities import are_items_in_list


__all__ = [
    'TwoColourableProjection',
]


class TwoColourableProjection(object):

    def __init__(self, quad_mesh):
        self.quad_mesh = quad_mesh
        self.results = None
        self.times = None

    def projection_4(self, kmax=1):
        """Projection of a coarse quad mesh to the closest two-colourable sub-spaces.

        Parameters
        ----------
        mesh : CoarseQuadMesh
            A coarse quad mesh.

        Returns
        -------
        results : dict
            The combination pointing to the its result.
            If the combination is valid, the result is a tuple of the the two-colourable mesh,
            the two-colourable network, and the network vertex colors.

        References
        ----------
        .. [1] Oval et al., *Topology Finding of Two-Colourable Quad-Mesh Patterns in Structural Design*. Submitted.

        """

        mesh = self.quad_mesh
        vertices, edges = mesh.strip_graph()
        if is_adjacency_two_colorable(adjacency_from_edges(edges)) is not None:
            self.results = True
            return True

        results = {}

        k = 0

        current_pool = [[skey] for skey in mesh.strips()]

        while k < kmax:
            k += 1
            next_pool = []

            for combination in current_pool:
                if len(combination) > 1:
                    combination = list(set([i for item in combination for i in item]))
                else:
                    combination = list(set(combination))

                if len(collateral_strip_deletions(mesh, combination)) > 0:
                    continue
                if len(total_boundary_deletions(mesh, combination)) > 0:
                    continue

                # delete strips in mesh and check validity
                copy_mesh = mesh.copy()
                delete_strips(copy_mesh, combination, preserve_boundaries=True)
                topological_validity = copy_mesh.is_manifold() and copy_mesh.euler() == mesh.euler()
                if not topological_validity:
                    pass

                # delete strip vertices in network and check colourability
                else:
                    new_vertices = {vkey: xyz for vkey, xyz in vertices.items() if vkey not in combination}
                    new_edges = [(u, v) for u, v in edges if u not in combination and v not in combination]
                    two_colourability = is_adjacency_two_colorable(adjacency_from_edges(new_edges))
                    if not two_colourability:
                        next_pool.append(combination)
                    else:
                        results[tuple(combination)] = (copy_mesh, (new_vertices, new_edges), two_colourability)

            current_pool = itertools.combinations(next_pool, 2)

        self.results = results

    def projection_1(self, kmax=1):
        """Projection of a coarse quad mesh to the closest two-colourable sub-spaces.

        Parameters
        ----------
        mesh : CoarseQuadMesh
            A coarse quad mesh.

        Returns
        -------
        results : dict
            The combination pointing to the its result.
            If the combination is valid, the result is a tuple of the the two-colourable mesh,
            the two-colourable network, and the network vertex colors.

        References
        ----------
        .. [1] Oval et al., *Topology Finding of Two-Colourable Quad-Mesh Patterns in Structural Design*. Submitted.

        """

        mesh = self.quad_mesh
        n = mesh.number_of_strips()

        vertices, edges = mesh.strip_graph()
        if is_adjacency_two_colorable(adjacency_from_edges(edges)) is not None:
            self.results = True
            return True

        relation = {}
        for k in range(n):

            for combination in itertools.combination(mesh.strips(), k):
                other_strips = list(mesh.strips())
                for skey in combination:
                    del other_strips[skey]
                # downsteam_combinations = itertools.combination(mesh.strips(), k)
                relation[combination] = []

        results = {}

        k = 0

        current_pool = [[skey] for skey in mesh.strips()]

        while k < kmax:
            k += 1
            next_pool = []

            for combination in current_pool:
                if len(combination) > 1:
                    combination = list(set([i for item in combination for i in item]))
                else:
                    combination = list(set(combination))

                if len(collateral_strip_deletions(mesh, combination)) > 0:
                    continue
                if len(total_boundary_deletions(mesh, combination)) > 0:
                    continue

                # delete strips in mesh and check validity
                copy_mesh = mesh.copy()
                delete_strips(copy_mesh, combination, preserve_boundaries=True)
                topological_validity = copy_mesh.is_manifold() and copy_mesh.euler() == mesh.euler()
                if not topological_validity:
                    pass

                # delete strip vertices in network and check colourability
                else:
                    new_vertices = {vkey: xyz for vkey, xyz in vertices.items() if vkey not in combination}
                    new_edges = [(u, v) for u, v in edges if u not in combination and v not in combination]
                    two_colourability = is_adjacency_two_colorable(adjacency_from_edges(new_edges))
                    if not two_colourability:
                        next_pool.append(combination)
                    else:
                        results[tuple(combination)] = (copy_mesh, (new_vertices, new_edges), two_colourability)

            current_pool = itertools.combinations(next_pool, 2)

        self.results = results

    def projection_2(self, kmax=1):
        """Projection of a coarse quad mesh to the closest two-colourable sub-spaces.

        Parameters
        ----------
        mesh : CoarseQuadMesh
            A coarse quad mesh.

        Returns
        -------
        results : dict
            The combination pointing to the its result.
            If the combination is valid, the result is a tuple of the the two-colourable mesh,
            the two-colourable network, and the network vertex colors.

        References
        ----------
        .. [1] Oval et al., *Topology Finding of Two-Colourable Quad-Mesh Patterns in Structural Design*. Submitted.

        """

        mesh = self.quad_mesh

        # result for input mesh
        vertices, edges = mesh.strip_graph()
        if is_adjacency_two_colorable(adjacency_from_edges(edges)) is not None:
            self.results = True
            return True

        results = {}

        # guarantee valid kmax
        n = mesh.number_of_strips()
        if kmax < 1 or kmax > n:
            kmax = n

        # start iteration
        k = 0
        discarding_combination = []
        while k < kmax:
            k += 1
            to_continue = False
            # at_least_one_valid_k = False
            # test all combinations of (n k) strips
            for combination in itertools.combinations(mesh.strips(), k):
                set_combi = set(combination)
                # check results from potential previous sub-combinations
                for disc_comb in discarding_combination:
                    if disc_comb.issubset(set_combi):
                        break

                if len(collateral_strip_deletions(mesh, combination)) > 0:
                    to_continue = True
                    continue

                if len(total_boundary_deletions(mesh, combination)) > 0:
                    discarding_combination.append(set(combination))
                    continue

                # delete strips in mesh and check validity
                copy_mesh = mesh.copy()
                delete_strips(copy_mesh, combination, preserve_boundaries=True)
                topological_validity = copy_mesh.is_manifold() and copy_mesh.euler() == mesh.euler()
                if not topological_validity:
                    discarding_combination.append(set(combination))

                # delete strip vertices in network and check colourability
                else:
                    new_vertices = {vkey: xyz for vkey, xyz in vertices.items() if vkey not in combination}
                    new_edges = [(u, v) for u, v in edges if u not in combination and v not in combination]
                    two_colourability = is_adjacency_two_colorable(adjacency_from_edges(new_edges))
                    if not two_colourability:
                        to_continue = True
                    else:
                        results[combination] = (copy_mesh, (new_vertices, new_edges), two_colourability)
                        discarding_combination.append(set(combination))

            if not to_continue:
                break

        self.results = results

    def projection(self, kmax=1):
        """Projection of a coarse quad mesh to the closest two-colourable sub-spaces.

        Parameters
        ----------
        mesh : CoarseQuadMesh
            A coarse quad mesh.

        Returns
        -------
        results : dict
            The combination pointing to the its result.
            If the combination is valid, the result is a tuple of the the two-colourable mesh,
            the two-colourable network, and the network vertex colors.

        References
        ----------
        .. [1] Oval et al., *Topology Finding of Two-Colourable Quad-Mesh Patterns in Structural Design*. Submitted.

        """

        mesh = self.quad_mesh

        # # result for input mesh
        # vertices, edges = mesh.strip_graph()
        # if is_adjacency_two_colorable(adjacency_from_edges(edges)) is not None:
        # 	self.results = True
        # 	return True

        results = {}

        # guarantee valid kmax
        n = mesh.number_of_strips()
        if kmax < 1 or kmax > n:
            kmax = n

        # start iteration
        k = 0
        while k < kmax:
            k += 1
            to_continue = False
            # test all combinations of (n k) strips
            for combination in itertools.combinations(mesh.strips(), k):
                # check results from potential previous sub-combinations
                for previous_combination in results:
                    if are_items_in_list(previous_combination, combination):
                        # if a sub-combination yielded an invalid topology do not pursue
                        if results[previous_combination] == 'invalid shape topology':
                            results[combination] = 'already invalid shape topology'
                            break
                        elif type(results[previous_combination]) == tuple:
                            results[combination] = 'already two-colourable'
                            break
                if combination in results:
                    continue

                if len(collateral_strip_deletions(mesh, combination)) > 0:
                    to_continue = True
                    continue

                if len(total_boundary_deletions(mesh, combination)) > 0:
                    results[combination] = 'invalid shape topology'
                    continue

                # delete strips in mesh and check validity
                copy_mesh = mesh.copy()
                copy_mesh.collect_strips()
                delete_strips(copy_mesh, combination, preserve_boundaries=True)
                topological_validity = copy_mesh.is_manifold() and copy_mesh.euler() == mesh.euler()
                if not topological_validity:
                    results[combination] = 'invalid shape topology'

                # delete strip vertices in network and check colourability
                else:
                    vertices, edges = copy_mesh.strip_graph()
                    two_colourability = is_adjacency_two_colorable(adjacency_from_edges(edges))
                    if not two_colourability:
                        results[combination] = 'not two-colourable'
                        to_continue = True
                    else:
                        results[combination] = (copy_mesh, (vertices, edges), two_colourability)

            if not to_continue:
                break

        return self.results

    def projection_0(self, kmax=1):
        """Projection of a coarse quad mesh to the closest two-colourable sub-spaces.

        Parameters
        ----------
        mesh : CoarseQuadMesh
            A coarse quad mesh.

        Returns
        -------
        results : dict
            The combination pointing to the its result.
            If the combination is valid, the result is a tuple of the the two-colourable mesh,
            the two-colourable network, and the network vertex colors.

        References
        ----------
        .. [1] Oval et al., *Topology Finding of Two-Colourable Quad-Mesh Patterns in Structural Design*. Submitted.

        """

        mesh = self.quad_mesh

        # result for input mesh
        vertices, edges = mesh.strip_graph()
        if is_adjacency_two_colorable(adjacency_from_edges(edges)) is not None:
            self.results = True
            return True

        results = {}

        # guarantee valid kmax
        n = mesh.number_of_strips()
        if kmax < 1 or kmax > n:
            kmax = n

        total_valid = 0
        # start iteration
        k = 0
        discarding_combination = []
        discarding_combination_type = {}
        while k < kmax:
            k += 1
            to_continue = False
            at_least_one_valid_k = False
            # test all combinations of (n k) strips
            for combination in itertools.combinations(mesh.strips(), k):
                set_combi = set(combination)
                # check results from potential previous sub-combinations
                for disc_comb in discarding_combination:
                    if disc_comb.issubset(set_combi):
                        # if are_items_in_list(previous_combination, combination):
                        # if a sub-combination yielded an invalid topology do not pursue
                        if discarding_combination_type[tuple(disc_comb)] == 'invalid shape topology':
                            results[combination] = 'already invalid shape topology'
                            break
                        elif discarding_combination_type[tuple(disc_comb)] == 'two-colourable':
                            results[combination] = 'already two-colourable'
                            break

                if len(collateral_strip_deletions(mesh, combination)) > 0:
                    results[combination] = 'collateral deletions'

                if len(total_boundary_deletions(mesh, combination)) > 0:
                    results[combination] = 'invalid shape topology'
                    discarding_combination.append(set(combination))
                    discarding_combination_type[tuple(combination)] = 'invalid shape topology'

                if combination in results:
                    continue

                # delete strips in mesh and check validity
                copy_mesh = mesh.copy()
                # copy_mesh.collect_strips()
                delete_strips(copy_mesh, combination, preserve_boundaries=True)
                topological_validity = copy_mesh.is_manifold() and copy_mesh.euler() == mesh.euler()
                if not topological_validity:
                    results[combination] = 'invalid shape topology'
                    discarding_combination.append(set(combination))
                    discarding_combination_type[tuple(combination)] = 'invalid shape topology'

                # delete strip vertices in network and check colourability
                else:
                    # vertices, edges = copy_mesh.strip_graph()
                    new_vertices = {vkey: xyz for vkey, xyz in vertices.items() if vkey not in combination}
                    new_edges = [(u, v) for u, v in edges if u not in combination and v not in combination]
                    two_colourability = is_adjacency_two_colorable(adjacency_from_edges(new_edges))
                    if not two_colourability:
                        results[combination] = 'not two-colourable'
                        to_continue = True
                    else:
                        results[combination] = (copy_mesh, (new_vertices, new_edges), two_colourability)
                        discarding_combination.append(set(combination))
                        discarding_combination_type[tuple(combination)] = 'two-colourable'
                        at_least_one_valid_k = True
                        total_valid += 1

            if not to_continue:
                break

        self.results = results
        self.times = (t1 - t0, t2 - t0, t3 - t0)

    # --------------------------------------------------------------------------
    # results
    # --------------------------------------------------------------------------

    def get_results(self):
        return self.results

    def two_coloured_meshes(self, kmax=1):
        self.projection_4(kmax)
        for strips, results in self.get_results().items():
            yield results[0]

    def strip_deletions_yielding_two_colourability(self):
        out = []
        for combination, result in self.get_results().items():
            if type(result) == tuple:
                out.append(combination)
        return out


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':
    pass

    import compas
    from compas_plotters.meshplotter import MeshPlotter

    # vertices = [
    # [1.9, 11.2, 0.0], [9.7, 9.0, 0.0], [4.3, 4.7, 0.0], [3.8, 13.2, 0.0], [1.9, 13.2, 0.0],
    # [4.7, 2.2, 0.0], [5.7, 9.4, 0.0], [9.1, 6.4, 0.0], [14.2, 5.2, 0.0], [14.2, 2.2, 0.0],
    # [14.2, 13.2, 0.0], [1.9, 2.2, 0.0], [4.1, 10.9, 0.0], [11.5, 5.0, 0.0], [11.4, 2.2, 0.0],
    # [5.7, 6.7, 0.0], [14.2, 10.2, 0.0], [1.9, 4.2, 0.0], [11.4, 13.2, 0.0], [11.7, 10.6, 0.0]]
    # faces = [[7, 15, 2, 13], [15, 6, 12, 2], [6, 1, 19, 12], [1, 7, 13, 19], [8, 16, 19, 13], [16, 10, 18, 19],
    #          [18, 3, 12, 19], [3, 4, 0, 12], [0, 17, 2, 12], [17, 11, 5, 2], [5, 14, 13, 2], [14, 9, 8, 13]]

    # vertices = [
    # [-332.0, -22.0, 0.0], [-332.0, -19.0, 0.0], [-332.0, -5.0, 0.0], [-332.0, -2.0, 0.0],
    # [-329.0, -22.0, 0.0], [-329.0, -19.0, 0.0], [-329.0, -5.0, 0.0], [-329.0, -2.0, 0.0],
    # [-324.0, -15.0, 0.0], [-324.0, -9.0, 0.0], [-318.0, -15.0, 0.0], [-318.0, -9.0, 0.0],
    # [-312.0, -22.0, 0.0], [-312.0, -19.0, 0.0], [-312.0, -5.0, 0.0], [-312.0, -2.0, 0.0],
    # [-305.0, -15.0, 0.0], [-305.0, -9.0, 0.0], [-299.0, -15.0, 0.0], [-299.0, -9.0, 0.0],
    # [-295.0, -22.0, 0.0], [-295.0, -19.0, 0.0], [-295.0, -5.0, 0.0], [-295.0, -2.0, 0.0],
    # [-292.0, -22.0, 0.0], [-292.0, -19.0, 0.0], [-292.0, -5.0, 0.0], [-292.0, -2.0, 0.0]]
    # faces = [
    # [16, 17, 14, 13], [14, 17, 19, 22], [21, 22, 19, 18], [21, 18, 16, 13], [8, 9, 6, 5],
    # [6, 9, 11, 14], [13, 14, 11, 10], [13, 10, 8, 5], [4, 5, 1, 0], [5, 6, 2, 1], [6, 7, 3, 2],
    # [14, 15, 7, 6], [22, 23, 15, 14], [12, 13, 5, 4], [20, 21, 13, 12], [26, 27, 23, 22], [25, 26, 22, 21], [24, 25, 21, 20]]

    # vertices = [[-10.0, -50.0, 0.0], [-10.0, -49.0, 0.0], [-10.0, -48.0, 0.0], [-10.0, -46.5, 0.0], [-10.0, -46.0, 0.0], [-10.0, -45.5, 0.0], [-10.0, -45.0, 0.0], [-10.0, -44.5, 0.0], [-10.0, -44.0, 0.0], [-10.0, -43.5, 0.0], [-10.0, -42.0, 0.0], [-10.0, -41.0, 0.0], [-10.0, -40.0, 0.0], [-9.5, -45.0, 0.0], [-9.4375, -45.1875, 0.0], [-9.4375, -44.8125, 0.0], [-9.375, -45.375, 0.0], [-9.375, -44.625, 0.0], [-9.3000001907348633, -45.0, 0.0], [-9.1730766296386719, -45.173076629638672, 0.0], [-9.1730766296386719, -44.826923370361328, 0.0], [-9.0, -50.0, 0.0], [-9.0, -49.0, 0.0], [-9.0, -48.0, 0.0], [-9.0, -46.5, 0.0], [-9.0, -45.0, 0.0], [-9.0, -43.5, 0.0], [-9.0, -42.0, 0.0], [-9.0, -41.0, 0.0], [-9.0, -40.0, 0.0], [-8.75, -45.75, 0.0], [-8.75, -44.25, 0.0], [-8.5, -45.0, 0.0], [-8.0, -50.0, 0.0], [-8.0, -49.0, 0.0], [-8.0, -48.0, 0.0], [-8.0, -46.25, 0.0], [-8.0, -45.599998474121094, 0.0], [-8.0, -45.0, 0.0], [-8.0, -44.400001525878906, 0.0], [-8.0, -43.75, 0.0], [-8.0, -42.0, 0.0], [-8.0, -41.0, 0.0], [-8.0, -40.0, 0.0], [-7.5, -45.5, 0.0], [-7.5, -45.0, 0.0], [-7.5, -44.5, 0.0], [-7.4137930870056152, -46.103446960449219, 0.0], [-7.4137930870056152, -43.896553039550781, 0.0], [-7.25, -47.25, 0.0], [-7.25, -42.75, 0.0], [-7.0, -46.0, 0.0], [-7.0, -45.0, 0.0], [-7.0, -44.0, 0.0], [-6.75, -45.75, 0.0], [-6.75, -45.25, 0.0], [-6.75, -44.75, 0.0], [-6.75, -44.25, 0.0], [-6.5, -50.0, 0.0], [-6.5, -49.0, 0.0], [-6.5, -46.5, 0.0], [-6.5, -45.5, 0.0], [-6.5, -45.0, 0.0], [-6.5, -44.5, 0.0], [-6.5, -43.5, 0.0], [-6.5, -41.0, 0.0], [-6.5, -40.0, 0.0], [-6.25, -48.0, 0.0], [-6.25, -46.25, 0.0], [-6.25, -45.25, 0.0], [-6.25, -44.75, 0.0], [-6.25, -43.75, 0.0], [-6.25, -42.0, 0.0], [-6.1034483909606934, -47.413791656494141, 0.0], [-6.1034483909606934, -42.586208343505859, 0.0], [-6.0, -50.0, 0.0], [-6.0, -47.0, 0.0], [-6.0, -46.0, 0.0], [-6.0, -45.0, 0.0], [-6.0, -44.0, 0.0], [-6.0, -43.0, 0.0], [-6.0, -40.0, 0.0], [-5.75, -48.75, 0.0], [-5.75, -46.75, 0.0], [-5.75, -45.75, 0.0], [-5.75, -44.25, 0.0], [-5.75, -43.25, 0.0], [-5.75, -41.25, 0.0], [-5.5999999046325684, -48.0, 0.0], [-5.5999999046325684, -42.0, 0.0], [-5.5, -50.0, 0.0], [-5.5, -47.5, 0.0], [-5.5, -46.5, 0.0], [-5.5, -45.5, 0.0], [-5.5, -44.5, 0.0], [-5.5, -43.5, 0.0], [-5.5, -42.5, 0.0], [-5.5, -40.0, 0.0], [-5.375, -49.375, 0.0], [-5.375, -40.625, 0.0], [-5.25, -46.75, 0.0], [-5.25, -46.25, 0.0], [-5.25, -43.75, 0.0], [-5.25, -43.25, 0.0], [-5.1875, -49.4375, 0.0], [-5.1875, -40.5625, 0.0], [-5.1730771064758301, -49.173076629638672, 0.0], [-5.1730771064758301, -40.826923370361328, 0.0], [-5.0, -50.0, 0.0], [-5.0, -49.5, 0.0], [-5.0, -49.299999237060547, 0.0], [-5.0, -49.0, 0.0], [-5.0, -48.5, 0.0], [-5.0, -48.0, 0.0], [-5.0, -47.5, 0.0], [-5.0, -47.0, 0.0], [-5.0, -46.5, 0.0], [-5.0, -46.0, 0.0], [-5.0, -45.0, 0.0], [-5.0, -44.0, 0.0], [-5.0, -43.5, 0.0], [-5.0, -43.0, 0.0], [-5.0, -42.5, 0.0], [-5.0, -42.0, 0.0], [-5.0, -41.5, 0.0], [-5.0, -41.0, 0.0], [-5.0, -40.700000762939453, 0.0], [-5.0, -40.5, 0.0], [-5.0, -40.0, 0.0], [-4.8269228935241699, -49.173076629638672, 0.0], [-4.8269228935241699, -40.826923370361328, 0.0], [-4.8125, -49.4375, 0.0], [-4.8125, -40.5625, 0.0], [-4.75, -46.75, 0.0], [-4.75, -46.25, 0.0], [-4.75, -43.75, 0.0], [-4.75, -43.25, 0.0], [-4.625, -49.375, 0.0], [-4.625, -40.625, 0.0], [-4.5, -50.0, 0.0], [-4.5, -47.5, 0.0], [-4.5, -46.5, 0.0], [-4.5, -45.5, 0.0], [-4.5, -44.5, 0.0], [-4.5, -43.5, 0.0], [-4.5, -42.5, 0.0], [-4.5, -40.0, 0.0], [-4.4000000953674316, -48.0, 0.0], [-4.4000000953674316, -42.0, 0.0], [-4.25, -48.75, 0.0], [-4.25, -46.75, 0.0], [-4.25, -45.75, 0.0], [-4.25, -44.25, 0.0], [-4.25, -43.25, 0.0], [-4.25, -41.25, 0.0], [-4.0, -50.0, 0.0], [-4.0, -47.0, 0.0], [-4.0, -46.0, 0.0], [-4.0, -45.0, 0.0], [-4.0, -44.0, 0.0], [-4.0, -43.0, 0.0], [-4.0, -40.0, 0.0], [-3.8965516090393066, -47.413791656494141, 0.0], [-3.8965516090393066, -42.586208343505859, 0.0], [-3.75, -48.0, 0.0], [-3.75, -46.25, 0.0], [-3.75, -45.25, 0.0], [-3.75, -44.75, 0.0], [-3.75, -43.75, 0.0], [-3.75, -42.0, 0.0], [-3.5, -50.0, 0.0], [-3.5, -49.0, 0.0], [-3.5, -46.5, 0.0], [-3.5, -45.5, 0.0], [-3.5, -45.0, 0.0], [-3.5, -44.5, 0.0], [-3.5, -43.5, 0.0], [-3.5, -41.0, 0.0], [-3.5, -40.0, 0.0], [-3.25, -45.75, 0.0], [-3.25, -45.25, 0.0], [-3.25, -44.75, 0.0], [-3.25, -44.25, 0.0], [-3.0, -46.0, 0.0], [-3.0, -45.0, 0.0], [-3.0, -44.0, 0.0], [-2.75, -47.25, 0.0], [-2.75, -42.75, 0.0], [-2.5862069129943848, -46.103446960449219, 0.0], [-2.5862069129943848, -43.896553039550781, 0.0], [-2.5, -45.5, 0.0], [-2.5, -45.0, 0.0], [-2.5, -44.5, 0.0], [-2.0, -50.0, 0.0], [-2.0, -49.0, 0.0], [-2.0, -48.0, 0.0], [-2.0, -46.25, 0.0], [-2.0, -45.599998474121094, 0.0], [-2.0, -45.0, 0.0], [-2.0, -44.400001525878906, 0.0], [-2.0, -43.75, 0.0], [-2.0, -42.0, 0.0], [-2.0, -41.0, 0.0], [-2.0, -40.0, 0.0], [-1.5, -45.0, 0.0], [-1.25, -45.75, 0.0], [-1.25, -44.25, 0.0], [-1.0, -50.0, 0.0], [-1.0, -49.0, 0.0], [-1.0, -48.0, 0.0], [-1.0, -46.5, 0.0], [-1.0, -45.0, 0.0], [-1.0, -43.5, 0.0], [-1.0, -42.0, 0.0], [-1.0, -41.0, 0.0], [-1.0, -40.0, 0.0], [-0.82692307233810425, -45.173076629638672, 0.0], [-0.82692307233810425, -44.826923370361328, 0.0], [-0.69999998807907104, -45.0, 0.0], [-0.625, -45.375, 0.0], [-0.625, -44.625, 0.0], [-0.5625, -45.1875, 0.0], [-0.5625, -44.8125, 0.0], [-0.5, -45.0, 0.0], [0.0, -45.5, 0.0], [0.0, -44.5, 0.0], [0.0, -50.0, 0.0], [0.0, -49.0, 0.0], [0.0, -48.0, 0.0], [0.0, -46.5, 0.0], [0.0, -46.0, 0.0], [0.0, -45.0, 0.0], [0.0, -44.0, 0.0], [0.0, -43.5, 0.0], [0.0, -42.0, 0.0], [0.0, -41.0, 0.0], [0.0, -40.0, 0.0]]
    # faces = [[97, 128, 127, 105], [127, 128, 146, 132], [138, 161, 178, 177], [177, 178, 203, 202], [5, 6, 13, 14], [6, 7, 15, 13], [8, 9, 26, 17], [9, 10, 27, 26], [108, 109, 131, 139], [90, 104, 109, 108], [58, 59, 98, 75], [33, 34, 59, 58], [222, 225, 231, 223], [221, 223, 231, 224], [210, 219, 230, 229], [209, 210, 229, 228], [21, 22, 34, 33], [137, 171, 170, 155], [170, 171, 194, 193], [193, 194, 208, 207], [208, 209, 228, 227], [212, 233, 232, 220], [212, 213, 234, 233], [213, 214, 235, 234], [202, 203, 215, 214], [65, 66, 81, 99], [42, 43, 66, 65], [28, 29, 43, 42], [10, 11, 28, 27], [3, 4, 16, 24], [2, 3, 24, 23], [1, 2, 23, 22], [26, 27, 41, 40], [27, 28, 42, 41], [41, 42, 65, 72], [41, 72, 74, 50], [169, 177, 202, 201], [163, 169, 201, 187], [201, 202, 214, 213], [200, 201, 213, 212], [187, 201, 200, 189], [195, 196, 210, 209], [186, 188, 196, 195], [194, 195, 209, 208], [164, 195, 194, 171], [162, 186, 195, 164], [34, 35, 67, 59], [35, 49, 73, 67], [22, 23, 35, 34], [23, 24, 36, 35], [35, 36, 47, 49], [40, 41, 50, 48], [78, 94, 118, 93], [93, 118, 142, 117], [94, 119, 143, 118], [118, 143, 158, 142], [87, 124, 123, 89], [123, 124, 154, 148], [87, 107, 125, 124], [124, 125, 130, 154], [81, 97, 105, 99], [132, 146, 161, 138], [79, 95, 102, 85], [71, 86, 95, 79], [63, 79, 85, 70], [57, 71, 79, 63], [30, 32, 38, 37], [31, 39, 38, 32], [19, 25, 32, 30], [20, 31, 32, 25], [7, 8, 17, 15], [4, 5, 14, 16], [61, 69, 84, 77], [54, 61, 77, 68], [77, 84, 101, 92], [68, 77, 92, 83], [112, 113, 147, 149], [82, 88, 113, 112], [111, 112, 149, 129], [82, 112, 111, 106], [75, 98, 104, 90], [131, 137, 155, 139], [134, 151, 157, 141], [141, 157, 165, 150], [151, 166, 173, 157], [157, 173, 179, 165], [152, 159, 175, 167], [159, 168, 182, 175], [135, 144, 159, 152], [144, 153, 168, 159], [198, 199, 206, 204], [197, 198, 204, 205], [204, 206, 217, 211], [204, 211, 216, 205], [220, 232, 225, 222], [219, 221, 224, 230], [65, 99, 107, 87], [130, 138, 177, 154], [214, 215, 236, 235], [11, 12, 29, 28], [65, 87, 89, 72], [119, 135, 152, 143], [148, 154, 177, 169], [85, 102, 119, 94], [16, 19, 30, 24], [17, 26, 31, 20], [0, 1, 22, 21], [24, 30, 37, 36], [70, 85, 94, 78], [26, 40, 39, 31], [69, 78, 93, 84], [129, 149, 171, 137], [59, 82, 106, 98], [207, 208, 227, 226], [147, 164, 171, 149], [84, 93, 117, 101], [59, 67, 88, 82], [117, 142, 151, 134], [206, 212, 220, 217], [205, 216, 219, 210], [199, 200, 212, 206], [142, 158, 166, 151], [196, 197, 205, 210], [143, 152, 167, 158], [48, 50, 64, 53], [53, 64, 71, 57], [50, 74, 80, 64], [64, 80, 86, 71], [160, 163, 187, 176], [153, 160, 176, 168], [176, 187, 189, 185], [168, 176, 185, 182], [172, 183, 188, 186], [165, 179, 183, 172], [156, 172, 186, 162], [150, 165, 172, 156], [49, 60, 76, 73], [60, 68, 83, 76], [47, 51, 60, 49], [51, 54, 68, 60], [96, 122, 121, 103], [86, 96, 103, 95], [74, 96, 86, 80], [145, 163, 160, 153], [136, 145, 153, 144], [44, 45, 52, 55], [44, 55, 61, 54], [44, 54, 51, 47], [46, 48, 53, 57], [46, 57, 63, 56], [114, 115, 133, 140], [133, 141, 150, 140], [140, 150, 156, 162], [73, 76, 83, 91], [83, 92, 100, 91], [181, 192, 191, 184], [175, 182, 192, 181], [182, 185, 189, 192], [179, 190, 188, 183], [173, 180, 190, 179], [121, 122, 145, 136], [45, 46, 56, 52], [91, 100, 115, 114], [180, 184, 191, 190], [72, 89, 96, 74], [89, 123, 122, 96], [122, 123, 148, 145], [145, 148, 169, 163], [189, 200, 199, 192], [191, 192, 199, 198], [190, 191, 198, 197], [188, 190, 197, 196], [140, 162, 164, 147], [113, 114, 140, 147], [88, 91, 114, 113], [67, 73, 91, 88], [36, 37, 44, 47], [37, 38, 45, 44], [38, 39, 46, 45], [39, 40, 48, 46], [107, 126, 130, 125], [99, 105, 126, 107], [126, 132, 138, 130], [103, 121, 136, 120], [95, 103, 120, 102], [56, 63, 70, 62], [52, 56, 62, 55], [18, 20, 25, 19], [15, 17, 20, 18], [14, 18, 19, 16], [55, 62, 69, 61], [92, 101, 116, 100], [100, 116, 133, 115], [106, 111, 129, 110], [98, 106, 110, 104], [110, 129, 137, 131], [116, 134, 141, 133], [166, 174, 180, 173], [174, 181, 184, 180], [167, 175, 181, 174], [120, 136, 144, 135], [211, 217, 218, 216], [217, 220, 222, 218], [216, 218, 221, 219], [105, 127, 132, 126], [102, 120, 135, 119], [13, 15, 18, 14], [62, 70, 78, 69], [104, 110, 131, 109], [101, 117, 134, 116], [218, 222, 223, 221], [158, 167, 174, 166]]

    vertices = [[-32.5, -38.0, 0.0], [-32.0, -48.0, 0.0], [-30.0, -45.5, 0.0], [-30.0, -39.0, 0.0], [-29.218000411987305, -49.925998687744141, 0.0], [-27.5, -40.0, 0.0], [-27.163999557495117, -51.347999572753906, 0.0], [-26.5, -46.0, 0.0], [-25.5, -52.5, 0.0], [-25.5, -42.5, 0.0], [-24.5, -47.5, 0.0], [-23.0, -43.5, 0.0], [-22.5, -49.0, 0.0], [-22.5, -38.0, 0.0], [-22.0, -36.25, 0.0], [-21.5, -34.5, 0.0], [-18.5, -41.5, 0.0], [-15.75, -42.0, 0.0], [-13.0, -42.5, 0.0]]
    faces = [[4, 6, 10, 7], [1, 4, 7, 2], [6, 8, 12, 10], [10, 12, 18, 17], [14, 17, 18, 15], [0, 3, 14, 15], [0, 2, 7, 3], [7, 10, 11, 9], [10, 17, 16, 11], [13, 16, 17, 14], [3, 5, 13, 14], [3, 7, 9, 5]]

    mesh = QuadMesh.from_vertices_and_faces(vertices, faces)

    plotter = MeshPlotter(mesh, figsize=(5.0, 5.0))
    plotter.draw_vertices(text='key')
    plotter.draw_edges()
    plotter.draw_faces()
    plotter.show()

    mesh.collect_strips()
    projection = TwoColourableProjection(mesh)
    print(projection.projection_4(kmax=5))
    # for i in projection.projection(kmax=2):
    #     print(projection.strip_deletions_yielding_two_colourability())
