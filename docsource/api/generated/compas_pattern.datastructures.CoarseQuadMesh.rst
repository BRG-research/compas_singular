.. rst-class:: detail

CoarseQuadMesh
============================================

.. currentmodule:: compas_pattern.datastructures

.. autoclass:: CoarseQuadMesh

    
    

    .. rubric:: Attributes

    .. autosummary::
    

    .. rubric:: Inherited Attributes

    .. autosummary::
    
        ~CoarseQuadMesh.adjacency
        ~CoarseQuadMesh.data
        ~CoarseQuadMesh.name

    
    

    
    

    .. rubric:: Methods

    .. autosummary::
        :toctree:

    
        ~CoarseQuadMesh.__init__
        ~CoarseQuadMesh.coarse_edge_dense_edges
        ~CoarseQuadMesh.densification
        ~CoarseQuadMesh.from_quad_mesh
        ~CoarseQuadMesh.get_polygonal_mesh
        ~CoarseQuadMesh.get_quad_mesh
        ~CoarseQuadMesh.get_strip_densities
        ~CoarseQuadMesh.get_strip_density
        ~CoarseQuadMesh.set_mesh_density_face_target
        ~CoarseQuadMesh.set_polygonal_mesh
        ~CoarseQuadMesh.set_quad_mesh
        ~CoarseQuadMesh.set_strip_density
        ~CoarseQuadMesh.set_strip_density_func
        ~CoarseQuadMesh.set_strip_density_target
        ~CoarseQuadMesh.set_strips_density
        ~CoarseQuadMesh.set_strips_density_func
        ~CoarseQuadMesh.set_strips_density_target

    .. rubric:: Inherited Methods

    .. autosummary::
        :toctree:

    
        ~CoarseQuadMesh.add_face
        ~CoarseQuadMesh.add_vertex
        ~CoarseQuadMesh.area
        ~CoarseQuadMesh.boundaries
        ~CoarseQuadMesh.boundary_kinks
        ~CoarseQuadMesh.bounding_box
        ~CoarseQuadMesh.bounding_box_xy
        ~CoarseQuadMesh.centroid
        ~CoarseQuadMesh.clear
        ~CoarseQuadMesh.collapse_edge
        ~CoarseQuadMesh.collect_polyedge
        ~CoarseQuadMesh.collect_polyedges
        ~CoarseQuadMesh.collect_strip
        ~CoarseQuadMesh.collect_strips
        ~CoarseQuadMesh.connected_components
        ~CoarseQuadMesh.copy
        ~CoarseQuadMesh.cull_vertices
        ~CoarseQuadMesh.delete_face
        ~CoarseQuadMesh.delete_face_in_strips
        ~CoarseQuadMesh.delete_vertex
        ~CoarseQuadMesh.dual
        ~CoarseQuadMesh.edge_attribute
        ~CoarseQuadMesh.edge_attributes
        ~CoarseQuadMesh.edge_coordinates
        ~CoarseQuadMesh.edge_direction
        ~CoarseQuadMesh.edge_faces
        ~CoarseQuadMesh.edge_length
        ~CoarseQuadMesh.edge_midpoint
        ~CoarseQuadMesh.edge_point
        ~CoarseQuadMesh.edge_strip
        ~CoarseQuadMesh.edge_vector
        ~CoarseQuadMesh.edges
        ~CoarseQuadMesh.edges_attribute
        ~CoarseQuadMesh.edges_attributes
        ~CoarseQuadMesh.edges_on_boundaries
        ~CoarseQuadMesh.edges_on_boundary
        ~CoarseQuadMesh.edges_where
        ~CoarseQuadMesh.edges_where_predicate
        ~CoarseQuadMesh.euler
        ~CoarseQuadMesh.face_adjacency
        ~CoarseQuadMesh.face_adjacency_halfedge
        ~CoarseQuadMesh.face_adjacency_vertices
        ~CoarseQuadMesh.face_area
        ~CoarseQuadMesh.face_aspect_ratio
        ~CoarseQuadMesh.face_attribute
        ~CoarseQuadMesh.face_attributes
        ~CoarseQuadMesh.face_center
        ~CoarseQuadMesh.face_centroid
        ~CoarseQuadMesh.face_coordinates
        ~CoarseQuadMesh.face_corners
        ~CoarseQuadMesh.face_curvature
        ~CoarseQuadMesh.face_degree
        ~CoarseQuadMesh.face_flatness
        ~CoarseQuadMesh.face_halfedges
        ~CoarseQuadMesh.face_max_degree
        ~CoarseQuadMesh.face_min_degree
        ~CoarseQuadMesh.face_neighborhood
        ~CoarseQuadMesh.face_neighbors
        ~CoarseQuadMesh.face_normal
        ~CoarseQuadMesh.face_opposite_edge
        ~CoarseQuadMesh.face_skewness
        ~CoarseQuadMesh.face_strips
        ~CoarseQuadMesh.face_vertex_ancestor
        ~CoarseQuadMesh.face_vertex_descendant
        ~CoarseQuadMesh.face_vertices
        ~CoarseQuadMesh.faces
        ~CoarseQuadMesh.faces_attribute
        ~CoarseQuadMesh.faces_attributes
        ~CoarseQuadMesh.faces_on_boundary
        ~CoarseQuadMesh.faces_where
        ~CoarseQuadMesh.faces_where_predicate
        ~CoarseQuadMesh.flip_cycles
        ~CoarseQuadMesh.from_data
        ~CoarseQuadMesh.from_json
        ~CoarseQuadMesh.from_lines
        ~CoarseQuadMesh.from_obj
        ~CoarseQuadMesh.from_off
        ~CoarseQuadMesh.from_pickle
        ~CoarseQuadMesh.from_ply
        ~CoarseQuadMesh.from_points
        ~CoarseQuadMesh.from_polygons
        ~CoarseQuadMesh.from_polyhedron
        ~CoarseQuadMesh.from_polylines
        ~CoarseQuadMesh.from_shape
        ~CoarseQuadMesh.from_stl
        ~CoarseQuadMesh.from_vertices_and_faces
        ~CoarseQuadMesh.genus
        ~CoarseQuadMesh.get_any_face
        ~CoarseQuadMesh.get_any_face_vertex
        ~CoarseQuadMesh.get_any_vertex
        ~CoarseQuadMesh.get_any_vertices
        ~CoarseQuadMesh.gkey_key
        ~CoarseQuadMesh.halfedge_face
        ~CoarseQuadMesh.has_edge
        ~CoarseQuadMesh.has_face
        ~CoarseQuadMesh.has_halfedge
        ~CoarseQuadMesh.has_vertex
        ~CoarseQuadMesh.index_key
        ~CoarseQuadMesh.insert_vertex
        ~CoarseQuadMesh.is_boundary_vertex_kink
        ~CoarseQuadMesh.is_connected
        ~CoarseQuadMesh.is_edge_on_boundary
        ~CoarseQuadMesh.is_empty
        ~CoarseQuadMesh.is_face_on_boundary
        ~CoarseQuadMesh.is_manifold
        ~CoarseQuadMesh.is_orientable
        ~CoarseQuadMesh.is_quadmesh
        ~CoarseQuadMesh.is_regular
        ~CoarseQuadMesh.is_strip_closed
        ~CoarseQuadMesh.is_trimesh
        ~CoarseQuadMesh.is_valid
        ~CoarseQuadMesh.is_vertex_connected
        ~CoarseQuadMesh.is_vertex_on_boundary
        ~CoarseQuadMesh.is_vertex_singular
        ~CoarseQuadMesh.key_gkey
        ~CoarseQuadMesh.key_index
        ~CoarseQuadMesh.normal
        ~CoarseQuadMesh.number_of_edges
        ~CoarseQuadMesh.number_of_faces
        ~CoarseQuadMesh.number_of_strips
        ~CoarseQuadMesh.number_of_vertices
        ~CoarseQuadMesh.polyedge_graph
        ~CoarseQuadMesh.polyedges
        ~CoarseQuadMesh.polylines
        ~CoarseQuadMesh.singularities
        ~CoarseQuadMesh.singularity_polyedge_decomposition
        ~CoarseQuadMesh.singularity_polyedges
        ~CoarseQuadMesh.singularity_polyline_decomposition
        ~CoarseQuadMesh.singularity_polylines
        ~CoarseQuadMesh.smooth_area
        ~CoarseQuadMesh.smooth_centroid
        ~CoarseQuadMesh.split_edge
        ~CoarseQuadMesh.split_face
        ~CoarseQuadMesh.strip_edge_midpoint_polyline
        ~CoarseQuadMesh.strip_edges
        ~CoarseQuadMesh.strip_face_centroid_polyline
        ~CoarseQuadMesh.strip_faces
        ~CoarseQuadMesh.strip_graph
        ~CoarseQuadMesh.strip_side_polyedges
        ~CoarseQuadMesh.strip_side_polylines
        ~CoarseQuadMesh.strips
        ~CoarseQuadMesh.substitute_vertex_in_strips
        ~CoarseQuadMesh.summary
        ~CoarseQuadMesh.to_data
        ~CoarseQuadMesh.to_json
        ~CoarseQuadMesh.to_lines
        ~CoarseQuadMesh.to_obj
        ~CoarseQuadMesh.to_off
        ~CoarseQuadMesh.to_pickle
        ~CoarseQuadMesh.to_ply
        ~CoarseQuadMesh.to_points
        ~CoarseQuadMesh.to_polygons
        ~CoarseQuadMesh.to_polylines
        ~CoarseQuadMesh.to_quadmesh
        ~CoarseQuadMesh.to_stl
        ~CoarseQuadMesh.to_trimesh
        ~CoarseQuadMesh.to_vertices_and_faces
        ~CoarseQuadMesh.transform
        ~CoarseQuadMesh.transformed
        ~CoarseQuadMesh.unify_cycles
        ~CoarseQuadMesh.unset_edge_attribute
        ~CoarseQuadMesh.unset_face_attribute
        ~CoarseQuadMesh.unset_vertex_attribute
        ~CoarseQuadMesh.update_default_edge_attributes
        ~CoarseQuadMesh.update_default_face_attributes
        ~CoarseQuadMesh.update_default_vertex_attributes
        ~CoarseQuadMesh.vertex_area
        ~CoarseQuadMesh.vertex_attribute
        ~CoarseQuadMesh.vertex_attributes
        ~CoarseQuadMesh.vertex_centroid
        ~CoarseQuadMesh.vertex_coordinates
        ~CoarseQuadMesh.vertex_curvature
        ~CoarseQuadMesh.vertex_degree
        ~CoarseQuadMesh.vertex_faces
        ~CoarseQuadMesh.vertex_index
        ~CoarseQuadMesh.vertex_laplacian
        ~CoarseQuadMesh.vertex_max_degree
        ~CoarseQuadMesh.vertex_min_degree
        ~CoarseQuadMesh.vertex_neighborhood
        ~CoarseQuadMesh.vertex_neighborhood_centroid
        ~CoarseQuadMesh.vertex_neighbors
        ~CoarseQuadMesh.vertex_normal
        ~CoarseQuadMesh.vertex_opposite_vertex
        ~CoarseQuadMesh.vertices
        ~CoarseQuadMesh.vertices_attribute
        ~CoarseQuadMesh.vertices_attributes
        ~CoarseQuadMesh.vertices_on_boundaries
        ~CoarseQuadMesh.vertices_on_boundary
        ~CoarseQuadMesh.vertices_where
        ~CoarseQuadMesh.vertices_where_predicate

    
    