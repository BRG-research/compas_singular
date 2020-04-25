.. rst-class:: detail

PseudoQuadMesh
============================================

.. currentmodule:: compas_pattern.datastructures

.. autoclass:: PseudoQuadMesh

    
    

    .. rubric:: Attributes

    .. autosummary::
    

    .. rubric:: Inherited Attributes

    .. autosummary::
    
        ~PseudoQuadMesh.adjacency
        ~PseudoQuadMesh.data
        ~PseudoQuadMesh.name

    
    

    
    

    .. rubric:: Methods

    .. autosummary::
        :toctree:

    
        ~PseudoQuadMesh.__init__
        ~PseudoQuadMesh.collect_strip
        ~PseudoQuadMesh.collect_strips
        ~PseudoQuadMesh.delete_face_in_strips
        ~PseudoQuadMesh.face_opposite_edge
        ~PseudoQuadMesh.face_strips
        ~PseudoQuadMesh.from_vertices_and_faces_with_face_poles
        ~PseudoQuadMesh.from_vertices_and_faces_with_poles
        ~PseudoQuadMesh.has_strip_poles
        ~PseudoQuadMesh.is_face_pseudo_quad
        ~PseudoQuadMesh.is_pole
        ~PseudoQuadMesh.is_strip_closed
        ~PseudoQuadMesh.is_vertex_full_pole
        ~PseudoQuadMesh.is_vertex_partial_pole
        ~PseudoQuadMesh.is_vertex_pole
        ~PseudoQuadMesh.is_vertex_singular
        ~PseudoQuadMesh.poles
        ~PseudoQuadMesh.singularity_polyedges
        ~PseudoQuadMesh.strip_faces
        ~PseudoQuadMesh.vertex_index
        ~PseudoQuadMesh.vertex_pole_faces

    .. rubric:: Inherited Methods

    .. autosummary::
        :toctree:

    
        ~PseudoQuadMesh.add_face
        ~PseudoQuadMesh.add_vertex
        ~PseudoQuadMesh.area
        ~PseudoQuadMesh.boundaries
        ~PseudoQuadMesh.boundary_kinks
        ~PseudoQuadMesh.bounding_box
        ~PseudoQuadMesh.bounding_box_xy
        ~PseudoQuadMesh.centroid
        ~PseudoQuadMesh.clear
        ~PseudoQuadMesh.collapse_edge
        ~PseudoQuadMesh.collect_polyedge
        ~PseudoQuadMesh.collect_polyedges
        ~PseudoQuadMesh.connected_components
        ~PseudoQuadMesh.copy
        ~PseudoQuadMesh.cull_vertices
        ~PseudoQuadMesh.delete_face
        ~PseudoQuadMesh.delete_vertex
        ~PseudoQuadMesh.dual
        ~PseudoQuadMesh.edge_attribute
        ~PseudoQuadMesh.edge_attributes
        ~PseudoQuadMesh.edge_coordinates
        ~PseudoQuadMesh.edge_direction
        ~PseudoQuadMesh.edge_faces
        ~PseudoQuadMesh.edge_length
        ~PseudoQuadMesh.edge_midpoint
        ~PseudoQuadMesh.edge_point
        ~PseudoQuadMesh.edge_strip
        ~PseudoQuadMesh.edge_vector
        ~PseudoQuadMesh.edges
        ~PseudoQuadMesh.edges_attribute
        ~PseudoQuadMesh.edges_attributes
        ~PseudoQuadMesh.edges_on_boundaries
        ~PseudoQuadMesh.edges_on_boundary
        ~PseudoQuadMesh.edges_where
        ~PseudoQuadMesh.edges_where_predicate
        ~PseudoQuadMesh.euler
        ~PseudoQuadMesh.face_adjacency
        ~PseudoQuadMesh.face_adjacency_halfedge
        ~PseudoQuadMesh.face_adjacency_vertices
        ~PseudoQuadMesh.face_area
        ~PseudoQuadMesh.face_aspect_ratio
        ~PseudoQuadMesh.face_attribute
        ~PseudoQuadMesh.face_attributes
        ~PseudoQuadMesh.face_center
        ~PseudoQuadMesh.face_centroid
        ~PseudoQuadMesh.face_coordinates
        ~PseudoQuadMesh.face_corners
        ~PseudoQuadMesh.face_curvature
        ~PseudoQuadMesh.face_degree
        ~PseudoQuadMesh.face_flatness
        ~PseudoQuadMesh.face_halfedges
        ~PseudoQuadMesh.face_max_degree
        ~PseudoQuadMesh.face_min_degree
        ~PseudoQuadMesh.face_neighborhood
        ~PseudoQuadMesh.face_neighbors
        ~PseudoQuadMesh.face_normal
        ~PseudoQuadMesh.face_skewness
        ~PseudoQuadMesh.face_vertex_ancestor
        ~PseudoQuadMesh.face_vertex_descendant
        ~PseudoQuadMesh.face_vertices
        ~PseudoQuadMesh.faces
        ~PseudoQuadMesh.faces_attribute
        ~PseudoQuadMesh.faces_attributes
        ~PseudoQuadMesh.faces_on_boundary
        ~PseudoQuadMesh.faces_where
        ~PseudoQuadMesh.faces_where_predicate
        ~PseudoQuadMesh.flip_cycles
        ~PseudoQuadMesh.from_data
        ~PseudoQuadMesh.from_json
        ~PseudoQuadMesh.from_lines
        ~PseudoQuadMesh.from_obj
        ~PseudoQuadMesh.from_off
        ~PseudoQuadMesh.from_pickle
        ~PseudoQuadMesh.from_ply
        ~PseudoQuadMesh.from_points
        ~PseudoQuadMesh.from_polygons
        ~PseudoQuadMesh.from_polyhedron
        ~PseudoQuadMesh.from_polylines
        ~PseudoQuadMesh.from_shape
        ~PseudoQuadMesh.from_stl
        ~PseudoQuadMesh.from_vertices_and_faces
        ~PseudoQuadMesh.genus
        ~PseudoQuadMesh.get_any_face
        ~PseudoQuadMesh.get_any_face_vertex
        ~PseudoQuadMesh.get_any_vertex
        ~PseudoQuadMesh.get_any_vertices
        ~PseudoQuadMesh.gkey_key
        ~PseudoQuadMesh.halfedge_face
        ~PseudoQuadMesh.has_edge
        ~PseudoQuadMesh.has_face
        ~PseudoQuadMesh.has_halfedge
        ~PseudoQuadMesh.has_vertex
        ~PseudoQuadMesh.index_key
        ~PseudoQuadMesh.insert_vertex
        ~PseudoQuadMesh.is_boundary_vertex_kink
        ~PseudoQuadMesh.is_connected
        ~PseudoQuadMesh.is_edge_on_boundary
        ~PseudoQuadMesh.is_empty
        ~PseudoQuadMesh.is_face_on_boundary
        ~PseudoQuadMesh.is_manifold
        ~PseudoQuadMesh.is_orientable
        ~PseudoQuadMesh.is_quadmesh
        ~PseudoQuadMesh.is_regular
        ~PseudoQuadMesh.is_trimesh
        ~PseudoQuadMesh.is_valid
        ~PseudoQuadMesh.is_vertex_connected
        ~PseudoQuadMesh.is_vertex_on_boundary
        ~PseudoQuadMesh.key_gkey
        ~PseudoQuadMesh.key_index
        ~PseudoQuadMesh.normal
        ~PseudoQuadMesh.number_of_edges
        ~PseudoQuadMesh.number_of_faces
        ~PseudoQuadMesh.number_of_strips
        ~PseudoQuadMesh.number_of_vertices
        ~PseudoQuadMesh.polyedge_graph
        ~PseudoQuadMesh.polyedges
        ~PseudoQuadMesh.polylines
        ~PseudoQuadMesh.singularities
        ~PseudoQuadMesh.singularity_polyedge_decomposition
        ~PseudoQuadMesh.singularity_polyline_decomposition
        ~PseudoQuadMesh.singularity_polylines
        ~PseudoQuadMesh.smooth_area
        ~PseudoQuadMesh.smooth_centroid
        ~PseudoQuadMesh.split_edge
        ~PseudoQuadMesh.split_face
        ~PseudoQuadMesh.strip_edge_midpoint_polyline
        ~PseudoQuadMesh.strip_edges
        ~PseudoQuadMesh.strip_face_centroid_polyline
        ~PseudoQuadMesh.strip_graph
        ~PseudoQuadMesh.strip_side_polyedges
        ~PseudoQuadMesh.strip_side_polylines
        ~PseudoQuadMesh.strips
        ~PseudoQuadMesh.substitute_vertex_in_strips
        ~PseudoQuadMesh.summary
        ~PseudoQuadMesh.to_data
        ~PseudoQuadMesh.to_json
        ~PseudoQuadMesh.to_lines
        ~PseudoQuadMesh.to_obj
        ~PseudoQuadMesh.to_off
        ~PseudoQuadMesh.to_pickle
        ~PseudoQuadMesh.to_ply
        ~PseudoQuadMesh.to_points
        ~PseudoQuadMesh.to_polygons
        ~PseudoQuadMesh.to_polylines
        ~PseudoQuadMesh.to_quadmesh
        ~PseudoQuadMesh.to_stl
        ~PseudoQuadMesh.to_trimesh
        ~PseudoQuadMesh.to_vertices_and_faces
        ~PseudoQuadMesh.transform
        ~PseudoQuadMesh.transformed
        ~PseudoQuadMesh.unify_cycles
        ~PseudoQuadMesh.unset_edge_attribute
        ~PseudoQuadMesh.unset_face_attribute
        ~PseudoQuadMesh.unset_vertex_attribute
        ~PseudoQuadMesh.update_default_edge_attributes
        ~PseudoQuadMesh.update_default_face_attributes
        ~PseudoQuadMesh.update_default_vertex_attributes
        ~PseudoQuadMesh.vertex_area
        ~PseudoQuadMesh.vertex_attribute
        ~PseudoQuadMesh.vertex_attributes
        ~PseudoQuadMesh.vertex_centroid
        ~PseudoQuadMesh.vertex_coordinates
        ~PseudoQuadMesh.vertex_curvature
        ~PseudoQuadMesh.vertex_degree
        ~PseudoQuadMesh.vertex_faces
        ~PseudoQuadMesh.vertex_laplacian
        ~PseudoQuadMesh.vertex_max_degree
        ~PseudoQuadMesh.vertex_min_degree
        ~PseudoQuadMesh.vertex_neighborhood
        ~PseudoQuadMesh.vertex_neighborhood_centroid
        ~PseudoQuadMesh.vertex_neighbors
        ~PseudoQuadMesh.vertex_normal
        ~PseudoQuadMesh.vertex_opposite_vertex
        ~PseudoQuadMesh.vertices
        ~PseudoQuadMesh.vertices_attribute
        ~PseudoQuadMesh.vertices_attributes
        ~PseudoQuadMesh.vertices_on_boundaries
        ~PseudoQuadMesh.vertices_on_boundary
        ~PseudoQuadMesh.vertices_where
        ~PseudoQuadMesh.vertices_where_predicate

    
    