.. rst-class:: detail

DecompositionRemap
============================================

.. currentmodule:: compas_pattern.algorithms

.. autoclass:: DecompositionRemap

    
    

    .. rubric:: Attributes

    .. autosummary::
    
        ~DecompositionRemap.srf_guid

    .. rubric:: Inherited Attributes

    .. autosummary::
    
        ~DecompositionRemap.adjacency
        ~DecompositionRemap.data
        ~DecompositionRemap.name

    
    

    
    

    .. rubric:: Methods

    .. autosummary::
        :toctree:

    
        ~DecompositionRemap.__init__
        ~DecompositionRemap.decomposition_curves
        ~DecompositionRemap.decomposition_delaunay
        ~DecompositionRemap.decomposition_mesh
        ~DecompositionRemap.decomposition_polysurface
        ~DecompositionRemap.decomposition_skeleton

    .. rubric:: Inherited Methods

    .. autosummary::
        :toctree:

    
        ~DecompositionRemap.add_face
        ~DecompositionRemap.add_vertex
        ~DecompositionRemap.area
        ~DecompositionRemap.boundaries
        ~DecompositionRemap.boundary_kinks
        ~DecompositionRemap.bounding_box
        ~DecompositionRemap.bounding_box_xy
        ~DecompositionRemap.branches
        ~DecompositionRemap.branches_boundary
        ~DecompositionRemap.branches_singularity_to_boundary
        ~DecompositionRemap.branches_singularity_to_singularity
        ~DecompositionRemap.branches_splitting_boundary_kinks
        ~DecompositionRemap.branches_splitting_collapsed_boundaries
        ~DecompositionRemap.branches_splitting_flipped_faces
        ~DecompositionRemap.centroid
        ~DecompositionRemap.clear
        ~DecompositionRemap.collapse_edge
        ~DecompositionRemap.connected_components
        ~DecompositionRemap.copy
        ~DecompositionRemap.corner_faces
        ~DecompositionRemap.corner_vertices
        ~DecompositionRemap.cull_vertices
        ~DecompositionRemap.decomposition_polyline
        ~DecompositionRemap.decomposition_polylines
        ~DecompositionRemap.delete_face
        ~DecompositionRemap.delete_vertex
        ~DecompositionRemap.dual
        ~DecompositionRemap.edge_attribute
        ~DecompositionRemap.edge_attributes
        ~DecompositionRemap.edge_coordinates
        ~DecompositionRemap.edge_direction
        ~DecompositionRemap.edge_faces
        ~DecompositionRemap.edge_length
        ~DecompositionRemap.edge_midpoint
        ~DecompositionRemap.edge_point
        ~DecompositionRemap.edge_vector
        ~DecompositionRemap.edges
        ~DecompositionRemap.edges_attribute
        ~DecompositionRemap.edges_attributes
        ~DecompositionRemap.edges_on_boundaries
        ~DecompositionRemap.edges_on_boundary
        ~DecompositionRemap.edges_where
        ~DecompositionRemap.edges_where_predicate
        ~DecompositionRemap.euler
        ~DecompositionRemap.face_adjacency
        ~DecompositionRemap.face_adjacency_halfedge
        ~DecompositionRemap.face_adjacency_vertices
        ~DecompositionRemap.face_area
        ~DecompositionRemap.face_aspect_ratio
        ~DecompositionRemap.face_attribute
        ~DecompositionRemap.face_attributes
        ~DecompositionRemap.face_center
        ~DecompositionRemap.face_centroid
        ~DecompositionRemap.face_coordinates
        ~DecompositionRemap.face_corners
        ~DecompositionRemap.face_curvature
        ~DecompositionRemap.face_degree
        ~DecompositionRemap.face_flatness
        ~DecompositionRemap.face_halfedges
        ~DecompositionRemap.face_max_degree
        ~DecompositionRemap.face_min_degree
        ~DecompositionRemap.face_neighborhood
        ~DecompositionRemap.face_neighbors
        ~DecompositionRemap.face_normal
        ~DecompositionRemap.face_skewness
        ~DecompositionRemap.face_vertex_ancestor
        ~DecompositionRemap.face_vertex_descendant
        ~DecompositionRemap.face_vertices
        ~DecompositionRemap.faces
        ~DecompositionRemap.faces_attribute
        ~DecompositionRemap.faces_attributes
        ~DecompositionRemap.faces_on_boundary
        ~DecompositionRemap.faces_where
        ~DecompositionRemap.faces_where_predicate
        ~DecompositionRemap.flip_cycles
        ~DecompositionRemap.from_data
        ~DecompositionRemap.from_json
        ~DecompositionRemap.from_lines
        ~DecompositionRemap.from_mesh
        ~DecompositionRemap.from_obj
        ~DecompositionRemap.from_off
        ~DecompositionRemap.from_pickle
        ~DecompositionRemap.from_ply
        ~DecompositionRemap.from_points
        ~DecompositionRemap.from_polygons
        ~DecompositionRemap.from_polyhedron
        ~DecompositionRemap.from_polylines
        ~DecompositionRemap.from_shape
        ~DecompositionRemap.from_skeleton
        ~DecompositionRemap.from_stl
        ~DecompositionRemap.from_vertices_and_faces
        ~DecompositionRemap.genus
        ~DecompositionRemap.get_any_face
        ~DecompositionRemap.get_any_face_vertex
        ~DecompositionRemap.get_any_vertex
        ~DecompositionRemap.get_any_vertices
        ~DecompositionRemap.gkey_key
        ~DecompositionRemap.halfedge_face
        ~DecompositionRemap.has_edge
        ~DecompositionRemap.has_face
        ~DecompositionRemap.has_halfedge
        ~DecompositionRemap.has_vertex
        ~DecompositionRemap.index_key
        ~DecompositionRemap.insert_vertex
        ~DecompositionRemap.is_boundary_vertex_kink
        ~DecompositionRemap.is_connected
        ~DecompositionRemap.is_edge_on_boundary
        ~DecompositionRemap.is_empty
        ~DecompositionRemap.is_face_on_boundary
        ~DecompositionRemap.is_manifold
        ~DecompositionRemap.is_orientable
        ~DecompositionRemap.is_quadmesh
        ~DecompositionRemap.is_regular
        ~DecompositionRemap.is_trimesh
        ~DecompositionRemap.is_valid
        ~DecompositionRemap.is_vertex_connected
        ~DecompositionRemap.is_vertex_on_boundary
        ~DecompositionRemap.key_gkey
        ~DecompositionRemap.key_index
        ~DecompositionRemap.lines
        ~DecompositionRemap.normal
        ~DecompositionRemap.number_of_edges
        ~DecompositionRemap.number_of_faces
        ~DecompositionRemap.number_of_vertices
        ~DecompositionRemap.quadrangulate_polygonal_faces
        ~DecompositionRemap.quadrangulate_polygonal_faces_wip
        ~DecompositionRemap.singular_faces
        ~DecompositionRemap.singular_points
        ~DecompositionRemap.smooth_area
        ~DecompositionRemap.smooth_centroid
        ~DecompositionRemap.solve_triangular_faces
        ~DecompositionRemap.split_edge
        ~DecompositionRemap.split_face
        ~DecompositionRemap.split_quads_with_poles
        ~DecompositionRemap.split_vertices
        ~DecompositionRemap.store_pole_data
        ~DecompositionRemap.summary
        ~DecompositionRemap.to_data
        ~DecompositionRemap.to_json
        ~DecompositionRemap.to_lines
        ~DecompositionRemap.to_obj
        ~DecompositionRemap.to_off
        ~DecompositionRemap.to_pickle
        ~DecompositionRemap.to_ply
        ~DecompositionRemap.to_points
        ~DecompositionRemap.to_polygons
        ~DecompositionRemap.to_polylines
        ~DecompositionRemap.to_quadmesh
        ~DecompositionRemap.to_stl
        ~DecompositionRemap.to_trimesh
        ~DecompositionRemap.to_vertices_and_faces
        ~DecompositionRemap.transform
        ~DecompositionRemap.transformed
        ~DecompositionRemap.unify_cycles
        ~DecompositionRemap.unset_edge_attribute
        ~DecompositionRemap.unset_face_attribute
        ~DecompositionRemap.unset_vertex_attribute
        ~DecompositionRemap.update_default_edge_attributes
        ~DecompositionRemap.update_default_face_attributes
        ~DecompositionRemap.update_default_vertex_attributes
        ~DecompositionRemap.vertex_area
        ~DecompositionRemap.vertex_attribute
        ~DecompositionRemap.vertex_attributes
        ~DecompositionRemap.vertex_centroid
        ~DecompositionRemap.vertex_coordinates
        ~DecompositionRemap.vertex_curvature
        ~DecompositionRemap.vertex_degree
        ~DecompositionRemap.vertex_faces
        ~DecompositionRemap.vertex_laplacian
        ~DecompositionRemap.vertex_max_degree
        ~DecompositionRemap.vertex_min_degree
        ~DecompositionRemap.vertex_neighborhood
        ~DecompositionRemap.vertex_neighborhood_centroid
        ~DecompositionRemap.vertex_neighbors
        ~DecompositionRemap.vertex_normal
        ~DecompositionRemap.vertices
        ~DecompositionRemap.vertices_attribute
        ~DecompositionRemap.vertices_attributes
        ~DecompositionRemap.vertices_on_boundaries
        ~DecompositionRemap.vertices_on_boundary
        ~DecompositionRemap.vertices_where
        ~DecompositionRemap.vertices_where_predicate

    
    