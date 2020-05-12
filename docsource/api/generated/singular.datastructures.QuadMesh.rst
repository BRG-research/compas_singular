.. rst-class:: detail

QuadMesh
================================

.. currentmodule:: singular.datastructures

.. autoclass:: QuadMesh

    
    

    .. rubric:: Attributes

    .. autosummary::
    

    .. rubric:: Inherited Attributes

    .. autosummary::
    
        ~QuadMesh.adjacency
        ~QuadMesh.data
        ~QuadMesh.name

    
    

    
    

    .. rubric:: Methods

    .. autosummary::
        :toctree:

    
        ~QuadMesh.__init__
        ~QuadMesh.collect_polyedge
        ~QuadMesh.collect_polyedges
        ~QuadMesh.collect_strip
        ~QuadMesh.collect_strips
        ~QuadMesh.delete_face_in_strips
        ~QuadMesh.edge_strip
        ~QuadMesh.face_opposite_edge
        ~QuadMesh.face_strips
        ~QuadMesh.is_polyedge_closed
        ~QuadMesh.is_strip_closed
        ~QuadMesh.is_vertex_singular
        ~QuadMesh.number_of_strips
        ~QuadMesh.polyedge_graph
        ~QuadMesh.polyedges
        ~QuadMesh.polylines
        ~QuadMesh.singularities
        ~QuadMesh.singularity_polyedge_decomposition
        ~QuadMesh.singularity_polyedges
        ~QuadMesh.singularity_polyline_decomposition
        ~QuadMesh.singularity_polylines
        ~QuadMesh.strip_edge_midpoint_polyline
        ~QuadMesh.strip_edges
        ~QuadMesh.strip_face_centroid_polyline
        ~QuadMesh.strip_faces
        ~QuadMesh.strip_graph
        ~QuadMesh.strip_side_polyedges
        ~QuadMesh.strip_side_polylines
        ~QuadMesh.strips
        ~QuadMesh.substitute_vertex_in_strips
        ~QuadMesh.vertex_index
        ~QuadMesh.vertex_opposite_vertex

    .. rubric:: Inherited Methods

    .. autosummary::
        :toctree:

    
        ~QuadMesh.add_face
        ~QuadMesh.add_vertex
        ~QuadMesh.area
        ~QuadMesh.boundaries
        ~QuadMesh.boundary_kinks
        ~QuadMesh.bounding_box
        ~QuadMesh.bounding_box_xy
        ~QuadMesh.centroid
        ~QuadMesh.clear
        ~QuadMesh.collapse_edge
        ~QuadMesh.connected_components
        ~QuadMesh.copy
        ~QuadMesh.cull_vertices
        ~QuadMesh.delete_face
        ~QuadMesh.delete_vertex
        ~QuadMesh.dual
        ~QuadMesh.edge_attribute
        ~QuadMesh.edge_attributes
        ~QuadMesh.edge_coordinates
        ~QuadMesh.edge_direction
        ~QuadMesh.edge_faces
        ~QuadMesh.edge_length
        ~QuadMesh.edge_midpoint
        ~QuadMesh.edge_point
        ~QuadMesh.edge_vector
        ~QuadMesh.edges
        ~QuadMesh.edges_attribute
        ~QuadMesh.edges_attributes
        ~QuadMesh.edges_on_boundaries
        ~QuadMesh.edges_on_boundary
        ~QuadMesh.edges_where
        ~QuadMesh.edges_where_predicate
        ~QuadMesh.euler
        ~QuadMesh.face_adjacency
        ~QuadMesh.face_adjacency_halfedge
        ~QuadMesh.face_adjacency_vertices
        ~QuadMesh.face_area
        ~QuadMesh.face_aspect_ratio
        ~QuadMesh.face_attribute
        ~QuadMesh.face_attributes
        ~QuadMesh.face_center
        ~QuadMesh.face_centroid
        ~QuadMesh.face_coordinates
        ~QuadMesh.face_corners
        ~QuadMesh.face_curvature
        ~QuadMesh.face_degree
        ~QuadMesh.face_flatness
        ~QuadMesh.face_halfedges
        ~QuadMesh.face_max_degree
        ~QuadMesh.face_min_degree
        ~QuadMesh.face_neighborhood
        ~QuadMesh.face_neighbors
        ~QuadMesh.face_normal
        ~QuadMesh.face_skewness
        ~QuadMesh.face_vertex_ancestor
        ~QuadMesh.face_vertex_descendant
        ~QuadMesh.face_vertices
        ~QuadMesh.faces
        ~QuadMesh.faces_attribute
        ~QuadMesh.faces_attributes
        ~QuadMesh.faces_on_boundary
        ~QuadMesh.faces_where
        ~QuadMesh.faces_where_predicate
        ~QuadMesh.flip_cycles
        ~QuadMesh.from_data
        ~QuadMesh.from_json
        ~QuadMesh.from_lines
        ~QuadMesh.from_obj
        ~QuadMesh.from_off
        ~QuadMesh.from_pickle
        ~QuadMesh.from_ply
        ~QuadMesh.from_points
        ~QuadMesh.from_polygons
        ~QuadMesh.from_polyhedron
        ~QuadMesh.from_polylines
        ~QuadMesh.from_shape
        ~QuadMesh.from_stl
        ~QuadMesh.from_vertices_and_faces
        ~QuadMesh.genus
        ~QuadMesh.get_any_face
        ~QuadMesh.get_any_face_vertex
        ~QuadMesh.get_any_vertex
        ~QuadMesh.get_any_vertices
        ~QuadMesh.gkey_key
        ~QuadMesh.halfedge_face
        ~QuadMesh.has_edge
        ~QuadMesh.has_face
        ~QuadMesh.has_halfedge
        ~QuadMesh.has_vertex
        ~QuadMesh.index_key
        ~QuadMesh.insert_vertex
        ~QuadMesh.is_boundary_vertex_kink
        ~QuadMesh.is_connected
        ~QuadMesh.is_edge_on_boundary
        ~QuadMesh.is_empty
        ~QuadMesh.is_face_on_boundary
        ~QuadMesh.is_manifold
        ~QuadMesh.is_orientable
        ~QuadMesh.is_quadmesh
        ~QuadMesh.is_regular
        ~QuadMesh.is_trimesh
        ~QuadMesh.is_valid
        ~QuadMesh.is_vertex_connected
        ~QuadMesh.is_vertex_on_boundary
        ~QuadMesh.key_gkey
        ~QuadMesh.key_index
        ~QuadMesh.normal
        ~QuadMesh.number_of_edges
        ~QuadMesh.number_of_faces
        ~QuadMesh.number_of_vertices
        ~QuadMesh.smooth_area
        ~QuadMesh.smooth_centroid
        ~QuadMesh.split_edge
        ~QuadMesh.split_face
        ~QuadMesh.summary
        ~QuadMesh.to_data
        ~QuadMesh.to_json
        ~QuadMesh.to_lines
        ~QuadMesh.to_obj
        ~QuadMesh.to_off
        ~QuadMesh.to_pickle
        ~QuadMesh.to_ply
        ~QuadMesh.to_points
        ~QuadMesh.to_polygons
        ~QuadMesh.to_polylines
        ~QuadMesh.to_quadmesh
        ~QuadMesh.to_stl
        ~QuadMesh.to_trimesh
        ~QuadMesh.to_vertices_and_faces
        ~QuadMesh.transform
        ~QuadMesh.transformed
        ~QuadMesh.unify_cycles
        ~QuadMesh.unset_edge_attribute
        ~QuadMesh.unset_face_attribute
        ~QuadMesh.unset_vertex_attribute
        ~QuadMesh.update_default_edge_attributes
        ~QuadMesh.update_default_face_attributes
        ~QuadMesh.update_default_vertex_attributes
        ~QuadMesh.vertex_area
        ~QuadMesh.vertex_attribute
        ~QuadMesh.vertex_attributes
        ~QuadMesh.vertex_centroid
        ~QuadMesh.vertex_coordinates
        ~QuadMesh.vertex_curvature
        ~QuadMesh.vertex_degree
        ~QuadMesh.vertex_faces
        ~QuadMesh.vertex_laplacian
        ~QuadMesh.vertex_max_degree
        ~QuadMesh.vertex_min_degree
        ~QuadMesh.vertex_neighborhood
        ~QuadMesh.vertex_neighborhood_centroid
        ~QuadMesh.vertex_neighbors
        ~QuadMesh.vertex_normal
        ~QuadMesh.vertices
        ~QuadMesh.vertices_attribute
        ~QuadMesh.vertices_attributes
        ~QuadMesh.vertices_on_boundaries
        ~QuadMesh.vertices_on_boundary
        ~QuadMesh.vertices_where
        ~QuadMesh.vertices_where_predicate

    
    