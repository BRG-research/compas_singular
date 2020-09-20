from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import time
import itertools

from compas.topology import adjacency_from_edges

# from ..datastructures import QuadMesh
from ..datastructures import delete_strips
from ..datastructures import collateral_strip_deletions
from ..datastructures import total_boundary_deletions
from ..topology import is_adjacency_two_colorable
from ..utilities import are_items_in_list


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

        t0 = time.time()
        k = 0

        current_pool = [[skey] for skey in mesh.strips()]

        while k < kmax:
            k += 1
            next_pool = []
            # print(current_pool)
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

        t1 = time.time()
        print(t1 - t0)

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

        t0 = time.time()
        k = 0

        current_pool = [[skey] for skey in mesh.strips()]

        while k < kmax:
            k += 1
            next_pool = []
            # print(current_pool)
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

        t1 = time.time()
        print(t1 - t0)

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

        t0 = time.time()

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

        t1 = time.time()
        print(t1 - t0)

        # print(results)
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

        t0 = time.time()
        t1 = - float('inf')
        t2 = - float('inf')
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
                        if t1 < 0:
                            t1 = time.time()

            if t2 < 0 and total_valid > 0 and not at_least_one_valid_k:
                t2 = time.time()

            if not to_continue:
                break

        t3 = time.time()
        print(len(discarding_combination))
        print(t3 - t0)
        self.results = results
        self.times = (t1 - t0, t2 - t0, t3 - t0)

    # --------------------------------------------------------------------------
    # results
    # --------------------------------------------------------------------------

    def get_results(self):
        return self.results

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

    # import compas
    # from compas_plotters.meshplotter import MeshPlotter

    # vertices = [
    # [1.9, 11.2, 0.0], [9.7, 9.0, 0.0], [4.3, 4.7, 0.0], [3.8, 13.2, 0.0], [1.9, 13.2, 0.0],
    # [4.7, 2.2, 0.0], [5.7, 9.4, 0.0], [9.1, 6.4, 0.0], [14.2, 5.2, 0.0], [14.2, 2.2, 0.0],
    # [14.2, 13.2, 0.0], [1.9, 2.2, 0.0], [4.1, 10.9, 0.0], [11.5, 5.0, 0.0], [11.4, 2.2, 0.0],
    # [5.7, 6.7, 0.0], [14.2, 10.2, 0.0], [1.9, 4.2, 0.0], [11.4, 13.2, 0.0], [11.7, 10.6, 0.0]]
    # faces = [[7, 15, 2, 13], [15, 6, 12, 2], [6, 1, 19, 12], [1, 7, 13, 19], [8, 16, 19, 13], [16, 10, 18, 19],
    #          [18, 3, 12, 19], [3, 4, 0, 12], [0, 17, 2, 12], [17, 11, 5, 2], [5, 14, 13, 2], [14, 9, 8, 13]]

    # vertices_1 = [
    # [-332.0, -22.0, 0.0], [-332.0, -19.0, 0.0], [-332.0, -5.0, 0.0], [-332.0, -2.0, 0.0],
    # [-329.0, -22.0, 0.0], [-329.0, -19.0, 0.0], [-329.0, -5.0, 0.0], [-329.0, -2.0, 0.0],
    # [-324.0, -15.0, 0.0], [-324.0, -9.0, 0.0], [-318.0, -15.0, 0.0], [-318.0, -9.0, 0.0],
    # [-312.0, -22.0, 0.0], [-312.0, -19.0, 0.0], [-312.0, -5.0, 0.0], [-312.0, -2.0, 0.0],
    # [-305.0, -15.0, 0.0], [-305.0, -9.0, 0.0], [-299.0, -15.0, 0.0], [-299.0, -9.0, 0.0],
    # [-295.0, -22.0, 0.0], [-295.0, -19.0, 0.0], [-295.0, -5.0, 0.0], [-295.0, -2.0, 0.0],
    # [-292.0, -22.0, 0.0], [-292.0, -19.0, 0.0], [-292.0, -5.0, 0.0], [-292.0, -2.0, 0.0]]
    # faces_1 = [
    # [16, 17, 14, 13], [14, 17, 19, 22], [21, 22, 19, 18], [21, 18, 16, 13], [8, 9, 6, 5],
    # [6, 9, 11, 14], [13, 14, 11, 10], [13, 10, 8, 5], [4, 5, 1, 0], [5, 6, 2, 1], [6, 7, 3, 2],
    # [14, 15, 7, 6], [22, 23, 15, 14], [12, 13, 5, 4], [20, 21, 13, 12], [26, 27, 23, 22], [25, 26, 22, 21], [24, 25, 21, 20]]

    # mesh = QuadMesh.from_vertices_and_faces(vertices, faces)

    # # plotter = MeshPlotter(mesh, figsize=(5.0, 5.0))
    # # plotter.draw_vertices(text='key')
    # # plotter.draw_edges()
    # # plotter.draw_faces()
    # # plotter.show()

    # mesh.collect_strips()
    # projection = TwoColourableProjection(mesh)
    # for i in projection.projection(kmax=5):
    #     print(projection.strip_deletions_yielding_two_colourability())
