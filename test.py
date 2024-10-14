import unittest
import src.config
from src.HalfEdgeMesh import HalfedgeMesh
from src.vertex import Vertex
from src.HalfEdge import Halfedge
from src.facet import Facet

class TestHalfedgeMesh(unittest.TestCase):

    def setUp(self):
        # Setup the initial mesh with some basic structure
        self.mesh = HalfedgeMesh()


        
        # Add vertices to the mesh
        self.mesh.vertices = [
            Vertex(10, 10, 0),
            Vertex(-10, 10, 1),
            Vertex(-10, -10, 2),
            Vertex(10, -10, 3)
        ]
        
        # Add a triangle face and halfedges
        halfedge_0 = Halfedge(None, None, None, 0, None, 0)
        halfedge_1 = Halfedge(None, None, None, 1, None, 1)
        halfedge_2 = Halfedge(None, None, None, 1, None, 2)
        halfedge_3 = Halfedge(None, None, None, 2, None, 3)
        halfedge_4 = Halfedge(None, None, None, 3, None, 4)
        halfedge_5 = Halfedge(None, None, None, 3, None, 5)
        
        halfedge_0.next = 1
        halfedge_1.next = 4
        halfedge_4.next = 0
        halfedge_2.next = 3
        halfedge_3.next = 5
        halfedge_5.next = 2
        
        halfedge_0.facet = 0
        halfedge_1.facet = 0
        halfedge_4.facet = 0
        halfedge_2.facet = 1
        halfedge_3.facet = 1
        halfedge_5.facet = 1
        
        halfedge_0.prev = 4
        halfedge_1.prev = 0
        halfedge_4.prev = 1
        halfedge_2.prev = 5
        halfedge_3.prev = 2
        halfedge_5.prev = 3

        halfedge_1.opposite = 5
        halfedge_5.opposite = 1
        
        self.mesh.halfedges = [halfedge_0, halfedge_1, halfedge_2, halfedge_3, halfedge_4, halfedge_5]
        facet = Facet(0, 1, 3, 0, 0)
        facet2 = Facet(1, 2, 3, 1, 3)
        self.mesh.facets = [facet, facet2]
        
    def test_add_vertex_in_triangle(self):
        new_vertex = Vertex(0.5, 0.5, 4, None)
        self.mesh.add_vertex(new_vertex)
        
        # Check if the vertex was added correctly
        self.assertEqual(self.mesh.vertices_count(), 5)
        
        # Check if 3 new faces were created
        self.assertEqual(self.mesh.faces_count(), 4)
    
    def test_add_vertex_on_segment(self):
        new_vertex = Vertex(0.0, 0.0, 4, None)  # This vertex lies on the edge between vertex 0 and vertex 1
        self.mesh.add_vertex(new_vertex)
        
        # Check if the vertex was added correctly
        self.assertEqual(self.mesh.vertices_count(), 5)
        
        # Check if 4 new faces were created
        self.assertEqual(self.mesh.faces_count(), 4)
    
    def test_point_orientation(self):
        # Test if point orientation is calculated correctly
        vertex = Vertex(0.5, 0.5, 4, None)
        halfedge = self.mesh.halfedges[0]
        orientation = self.mesh.point_orientation(vertex, halfedge)
        self.assertEqual(orientation, "left")
        
        # Test a point on the segment
        vertex_on_segment = Vertex(0.0, 10.0, 0, None)
        orientation_on_segment = self.mesh.point_orientation(vertex_on_segment, halfedge)
        self.assertEqual(orientation_on_segment, "on_segment")

    def test_locate_triangle(self):
        # Add a new vertex inside the triangle
        new_vertex = Vertex(0.5, 0.5, 4, None)
        halfedge = self.mesh.locate_triangle(new_vertex)
        
        # Check if the correct halfedge was returned
        self.assertIsNotNone(halfedge)
        self.assertIn(halfedge.vertex, [0, 1, 3])  # Verify that it's pointing to vertex 0

if __name__ == '__main__':
    unittest.main()
