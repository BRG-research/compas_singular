.. rst-class:: detail

SkeletonDecomposition
===============================================

.. currentmodule:: compas_pattern.algorithms

.. autoclass:: SkeletonDecomposition

    
    

    .. rubric:: Attributes

    .. autosummary::
    

    .. rubric:: Inherited Attributes

    .. autosummary::
    
        ~SkeletonDecomposition.adjacency
        ~SkeletonDecomposition.data
        ~SkeletonDecomposition.name

    
    

    
    

    .. rubric:: Methods

    .. autosummary::
        :toctree:

    
        ~SkeletonDecomposition.__init__
        ~SkeletonDecomposition.branches_boundary
        ~SkeletonDecomposition.branches_singularity_to_boundary
        ~SkeletonDecomposition.branches_singularity_to_singularity
        ~SkeletonDecomposition.branches_splitting_boundary_kinks
        ~SkeletonDecomposition.branches_splitting_collapsed_boundaries
        ~SkeletonDecomposition.branches_splitting_flipped_faces
        ~SkeletonDecomposition.corner_faces
        ~SkeletonDecomposition.corner_vertices
        ~SkeletonDecomposition.decomposition_mesh
        ~SkeletonDecomposition.decomposition_polyline
        ~SkeletonDecomposition.decomposition_polylines
        ~SkeletonDecomposition.from_mesh
        ~SkeletonDecomposition.from_skeleton
        ~SkeletonDecomposition.quadrangulate_polygonal_faces
        ~SkeletonDecomposition.quadrangulate_polygonal_faces_wip
        ~SkeletonDecomposition.solve_triangular_faces
        ~SkeletonDecomposition.split_quads_with_poles
        ~SkeletonDecomposition.split_vertices
        ~SkeletonDecomposition.store_pole_data

    .. rubric:: Inherited Methods

    .. autosummary::
        :toctree:

    
        ~SkeletonDecomposition.add_face
        ~SkeletonDecomposition.add_vertex
        ~SkeletonDecomposition.area
        ~SkeletonDecomposition.boundaries
        ~SkeletonDecomposition.boundary_kinks
        ~SkeletonDecomposition.branches
        ~SkeletonDecomposition.centroid
        ~SkeletonDecomposition.clear
        ~SkeletonDecomposition.clear_facedict
        ~SkeletonDecomposition.clear_halfedgedict
        ~SkeletonDecomposition.clear_vertexdict
        ~SkeletonDecomposition.copy
        ~SkeletonDecomposition.cull_edges
        ~SkeletonDecomposition.cull_vertices
        ~SkeletonDecomposition.delete_face
        ~SkeletonDecomposition.delete_vertex
        ~SkeletonDecomposition.dump
        ~SkeletonDecomposition.dumps
        ~SkeletonDecomposition.edge_coordinates
        ~SkeletonDecomposition.edge_direction
        ~SkeletonDecomposition.edge_faces
        ~SkeletonDecomposition.edge_label_name
        ~SkeletonDecomposition.edge_length
        ~SkeletonDecomposition.edge_midpoint
        ~SkeletonDecomposition.edge_name
        ~SkeletonDecomposition.edge_point
        ~SkeletonDecomposition.edge_vector
        ~SkeletonDecomposition.edges
        ~SkeletonDecomposition.edges_on_boundary
        ~SkeletonDecomposition.edges_where
        ~SkeletonDecomposition.edges_where_predicate
        ~SkeletonDecomposition.euler
        ~SkeletonDecomposition.face_adjacency_halfedge
        ~SkeletonDecomposition.face_adjacency_vertices
        ~SkeletonDecomposition.face_area
        ~SkeletonDecomposition.face_aspect_ratio
        ~SkeletonDecomposition.face_center
        ~SkeletonDecomposition.face_centroid
        ~SkeletonDecomposition.face_coordinates
        ~SkeletonDecomposition.face_corners
        ~SkeletonDecomposition.face_curvature
        ~SkeletonDecomposition.face_degree
        ~SkeletonDecomposition.face_flatness
        ~SkeletonDecomposition.face_halfedges
        ~SkeletonDecomposition.face_label_name
        ~SkeletonDecomposition.face_max_degree
        ~SkeletonDecomposition.face_min_degree
        ~SkeletonDecomposition.face_name
        ~SkeletonDecomposition.face_neighborhood
        ~SkeletonDecomposition.face_neighbors
        ~SkeletonDecomposition.face_normal
        ~SkeletonDecomposition.face_skewness
        ~SkeletonDecomposition.face_vertex_ancestor
        ~SkeletonDecomposition.face_vertex_descendant
        ~SkeletonDecomposition.face_vertices
        ~SkeletonDecomposition.faces
        ~SkeletonDecomposition.faces_on_boundary
        ~SkeletonDecomposition.faces_where
        ~SkeletonDecomposition.faces_where_predicate
        ~SkeletonDecomposition.from_data
        ~SkeletonDecomposition.from_json
        ~SkeletonDecomposition.from_lines
        ~SkeletonDecomposition.from_obj
        ~SkeletonDecomposition.from_off
        ~SkeletonDecomposition.from_pickle
        ~SkeletonDecomposition.from_ply
        ~SkeletonDecomposition.from_points
        ~SkeletonDecomposition.from_polygons
        ~SkeletonDecomposition.from_polyhedron
        ~SkeletonDecomposition.from_polylines
        ~SkeletonDecomposition.from_shape
        ~SkeletonDecomposition.from_stl
        ~SkeletonDecomposition.from_vertices_and_faces
        ~SkeletonDecomposition.genus
        ~SkeletonDecomposition.get_any_edge
        ~SkeletonDecomposition.get_any_face
        ~SkeletonDecomposition.get_any_face_vertex
        ~SkeletonDecomposition.get_any_vertex
        ~SkeletonDecomposition.get_any_vertices
        ~SkeletonDecomposition.get_edge_attribute
        ~SkeletonDecomposition.get_edge_attributes
        ~SkeletonDecomposition.get_edges_attribute
        ~SkeletonDecomposition.get_edges_attributes
        ~SkeletonDecomposition.get_face_attribute
        ~SkeletonDecomposition.get_face_attributes
        ~SkeletonDecomposition.get_face_attributes_all
        ~SkeletonDecomposition.get_faces_attribute
        ~SkeletonDecomposition.get_faces_attributes
        ~SkeletonDecomposition.get_faces_attributes_all
        ~SkeletonDecomposition.get_vertex_attribute
        ~SkeletonDecomposition.get_vertex_attributes
        ~SkeletonDecomposition.get_vertices_attribute
        ~SkeletonDecomposition.get_vertices_attributes
        ~SkeletonDecomposition.gkey_key
        ~SkeletonDecomposition.has_edge
        ~SkeletonDecomposition.has_vertex
        ~SkeletonDecomposition.index_key
        ~SkeletonDecomposition.index_uv
        ~SkeletonDecomposition.insert_vertex
        ~SkeletonDecomposition.is_boundary_vertex_kink
        ~SkeletonDecomposition.is_edge_on_boundary
        ~SkeletonDecomposition.is_empty
        ~SkeletonDecomposition.is_face_on_boundary
        ~SkeletonDecomposition.is_manifold
        ~SkeletonDecomposition.is_orientable
        ~SkeletonDecomposition.is_quadmesh
        ~SkeletonDecomposition.is_regular
        ~SkeletonDecomposition.is_trimesh
        ~SkeletonDecomposition.is_valid
        ~SkeletonDecomposition.is_vertex_connected
        ~SkeletonDecomposition.is_vertex_on_boundary
        ~SkeletonDecomposition.key_gkey
        ~SkeletonDecomposition.key_index
        ~SkeletonDecomposition.leaves
        ~SkeletonDecomposition.lines
        ~SkeletonDecomposition.load
        ~SkeletonDecomposition.loads
        ~SkeletonDecomposition.normal
        ~SkeletonDecomposition.number_of_edges
        ~SkeletonDecomposition.number_of_faces
        ~SkeletonDecomposition.number_of_vertices
        ~SkeletonDecomposition.set_edge_attribute
        ~SkeletonDecomposition.set_edge_attributes
        ~SkeletonDecomposition.set_edges_attribute
        ~SkeletonDecomposition.set_edges_attributes
        ~SkeletonDecomposition.set_face_attribute
        ~SkeletonDecomposition.set_face_attributes
        ~SkeletonDecomposition.set_faces_attribute
        ~SkeletonDecomposition.set_faces_attributes
        ~SkeletonDecomposition.set_vertex_attribute
        ~SkeletonDecomposition.set_vertex_attributes
        ~SkeletonDecomposition.set_vertices_attribute
        ~SkeletonDecomposition.set_vertices_attributes
        ~SkeletonDecomposition.singular_faces
        ~SkeletonDecomposition.singular_points
        ~SkeletonDecomposition.summary
        ~SkeletonDecomposition.to_data
        ~SkeletonDecomposition.to_json
        ~SkeletonDecomposition.to_obj
        ~SkeletonDecomposition.to_pickle
        ~SkeletonDecomposition.to_vertices_and_faces
        ~SkeletonDecomposition.update_default_edge_attributes
        ~SkeletonDecomposition.update_default_face_attributes
        ~SkeletonDecomposition.update_default_vertex_attributes
        ~SkeletonDecomposition.uv_index
        ~SkeletonDecomposition.vertex_area
        ~SkeletonDecomposition.vertex_centroid
        ~SkeletonDecomposition.vertex_coordinates
        ~SkeletonDecomposition.vertex_curvature
        ~SkeletonDecomposition.vertex_degree
        ~SkeletonDecomposition.vertex_faces
        ~SkeletonDecomposition.vertex_label_name
        ~SkeletonDecomposition.vertex_laplacian
        ~SkeletonDecomposition.vertex_max_degree
        ~SkeletonDecomposition.vertex_min_degree
        ~SkeletonDecomposition.vertex_name
        ~SkeletonDecomposition.vertex_neighborhood
        ~SkeletonDecomposition.vertex_neighborhood_centroid
        ~SkeletonDecomposition.vertex_neighbors
        ~SkeletonDecomposition.vertex_normal
        ~SkeletonDecomposition.vertices
        ~SkeletonDecomposition.vertices_on_boundaries
        ~SkeletonDecomposition.vertices_on_boundary
        ~SkeletonDecomposition.vertices_where
        ~SkeletonDecomposition.vertices_where_predicate

    
    