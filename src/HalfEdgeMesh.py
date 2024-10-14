from .vertex import Vertex
from .facet import Facet
from .HalfEdge import Halfedge
from .alg import is_point_in_circumcircle, cross_product
import sys
import math
import random


class HalfedgeMesh:

    def __init__(self, filename=None, vertices=[], halfedges=[], facets=[]):
        """Make an empty halfedge mesh.

           filename   - a string that holds the directory location and name of
               the mesh
            vertices  - a list of Vertex types
            halfedges - a list of HalfEdge types
            facets    - a list of Facet types
        """

        self.vertices = vertices
        self.halfedges = halfedges
        self.facets = facets
        self.restricctions = []
        # dictionary of all the edges given indexes
        # TODO: Figure out if I need halfedges or if I should just use edges
        # Which is faster?

        
            
    def faces_count(self):
        count = 0
        for face in self.facets:
            if not face.deleted:
                count += 1
        return count
    
    def half_edges_count(self):
        count = 0
        for he in self.halfedges:
            if not he.deleted:
                count += 1
        return count

    def vertices_count(self):
        count = 0
        for vertex in self.vertices:
            if not vertex.deleted:
                count += 1
        return count

    def add_vertex(self, new_vertex):
        """
        Add a vertex to the HalfEdgeMesh, update faces and halfedges.
        
        new_vertex - Vertex object to be added.
        """
        for v in self.vertices:
            if v.x == new_vertex.x and v.y == new_vertex.y:
                return v

        # Step 1: Locate the triangle containing the new vertex
        halfedge_a = self.locate_triangle(new_vertex)
        if halfedge_a is None:
            raise ValueError("The vertex lies outside of the mesh.")

        halfedge_b = self.halfedges[halfedge_a.next]
        halfedge_c = self.halfedges[halfedge_b.next]

        orientation = self.point_orientation(new_vertex, halfedge_a)
        if orientation == 0:
            self.create_four_new_faces(halfedge_a, halfedge_b, halfedge_c, new_vertex)
        else:
            self.create_three_new_faces(halfedge_a, halfedge_b, halfedge_c, new_vertex)
        return new_vertex
    
    def add_restriction(self, new_v1, new_v2):
        v1 = self.add_vertex(new_v1)
        v2 = self.add_vertex(new_v2)

        while True:
            for halfedge in self.halfedges:
                if halfedge.opposite != None:
                    opp = self.halfedges[halfedge.opposite]
                    if (halfedge.vertex == v1.index and opp.vertex == v2.index) or (halfedge.vertex == v2.index and opp.vertex == v1.index):
                        halfedge.is_restricted = True
                        opp.is_restricted = True
                        return
                    if self.edges_intersect(v1, v2, halfedge):
                        self.flip_edge(halfedge, True)
        
    def create_three_new_faces(self, halfedge_a, halfedge_b, halfedge_c, new_vertex):
        new_vertex.index = len(self.vertices)
        self.vertices.append(new_vertex)
        # Step 2: Subdivide the triangle into three new triangles
        # Get the halfedges of the containing triangle
        # halfedge_a = self.halfedges[containing_triangle.halfedge]

        # Create new halfedges connecting the new vertex with the vertices of the triangle
        n_halfedges = len(self.halfedges)
        new_halfedge_a = Halfedge(None, None, None, halfedge_b.vertex, None, n_halfedges)
        new_halfedge_at = Halfedge(None, None, None, new_vertex.index, None, n_halfedges + 1)
        new_halfedge_b = Halfedge(None, None, None, halfedge_c.vertex, None, n_halfedges + 2)
        new_halfedge_bt = Halfedge(None, None, None, new_vertex.index, None, n_halfedges + 3)
        new_halfedge_c = Halfedge(None, None, None, halfedge_a.vertex, None, n_halfedges + 4)
        new_halfedge_ct = Halfedge(None, None, None, new_vertex.index, None, n_halfedges + 5)
        new_vertex.halfedge = n_halfedges

        # Update the current halfedges to point to the new halfedges
        halfedge_a.next = new_halfedge_a.index
        new_halfedge_a.next = new_halfedge_ct.index
        new_halfedge_ct.next = halfedge_a.index
        halfedge_b.next = new_halfedge_b.index
        new_halfedge_b.next = new_halfedge_at.index
        new_halfedge_at.next = halfedge_b.index
        halfedge_c.next = new_halfedge_c.index
        new_halfedge_c.next = new_halfedge_bt.index
        new_halfedge_bt.next = halfedge_c.index
        
        halfedge_a.prev = new_halfedge_ct.index
        new_halfedge_a.prev = halfedge_a.index
        new_halfedge_ct.prev = new_halfedge_a.index
        halfedge_b.prev = new_halfedge_at.index
        new_halfedge_b.prev = halfedge_b.index
        new_halfedge_at.prev = new_halfedge_b.index
        halfedge_c.prev = new_halfedge_bt.index
        new_halfedge_c.prev = halfedge_c.index
        new_halfedge_bt.prev = new_halfedge_c.index

        new_halfedge_a.opposite = new_halfedge_at.index
        new_halfedge_at.opposite = new_halfedge_a.index
        new_halfedge_b.opposite = new_halfedge_bt.index
        new_halfedge_bt.opposite = new_halfedge_b.index
        new_halfedge_c.opposite = new_halfedge_ct.index
        new_halfedge_ct.opposite = new_halfedge_c.index

        # Step 3: Create new faces
        new_facet_1 = Facet(halfedge_a.vertex, halfedge_b.vertex, new_vertex.index, len(self.facets) , new_halfedge_a)
        new_facet_2 = Facet(halfedge_b.vertex, halfedge_c.vertex, new_vertex.index, len(self.facets) + 1, new_halfedge_b)
        new_facet_3 = Facet(halfedge_c.vertex, halfedge_a.vertex, new_vertex.index, len(self.facets) + 2, new_halfedge_c)

        # Set the halfedges for the new faces
        act_facet = self.facets[halfedge_a.facet]
        act_facet.deleted = True
        halfedge_a.facet = new_facet_1.index
        new_halfedge_a.facet = new_facet_1.index
        new_halfedge_ct.facet = new_facet_1.index

        halfedge_b.facet = new_facet_2.index
        new_halfedge_b.facet = new_facet_2.index
        new_halfedge_at.facet = new_facet_2.index
        
        halfedge_c.facet = new_facet_3.index
        new_halfedge_c.facet = new_facet_3.index
        new_halfedge_bt.facet = new_facet_3.index

        # set facets half edges
        new_facet_1.halfedge = halfedge_a.index
        new_facet_2.halfedge = halfedge_b.index
        new_facet_3.halfedge = halfedge_c.index

        # Step 4: Add the new vertex and halfedges to the mesh
        self.halfedges.extend([new_halfedge_a, new_halfedge_at, new_halfedge_b, new_halfedge_bt, new_halfedge_c, new_halfedge_ct])
        self.facets.extend([new_facet_1, new_facet_2, new_facet_3])

        # Step 5: Ensure the Delaunay condition holds
        self.flip_edges_if_needed(halfedge_a)
        self.flip_edges_if_needed(halfedge_b)
        self.flip_edges_if_needed(halfedge_c)

    def create_four_new_faces(self, halfedge_a, halfedge_b, halfedge_c, new_vertex):
        new_vertex.index = len(self.vertices)
        self.vertices.append(new_vertex)
        # Step 2: Subdivide the triangle into four new triangles
        # Get the halfedges of the containing triangle
        halfedge_d = self.halfedges[halfedge_a.opposite]
        halfedge_e = self.halfedges[halfedge_d.next]
        halfedge_f = self.halfedges[halfedge_e.next]

        # Create new halfedges connecting the new vertex with the vertices of the triangle
        n_halfedges = len(self.halfedges)
        new_halfedge_a = Halfedge(None, None, None, halfedge_a.vertex, None, n_halfedges)
        new_halfedge_at = Halfedge(None, None, None, new_vertex.index, None, n_halfedges+1)
        new_halfedge_b = Halfedge(None, None, None, new_vertex.index, None, n_halfedges+2)
        new_halfedge_bt = Halfedge(None, None, None, halfedge_d.vertex, None, n_halfedges+3)
        
        new_halfedge_c = Halfedge(None, None, None, halfedge_c.vertex, None, n_halfedges+4)
        new_halfedge_ct = Halfedge(None, None, None, new_vertex.index, None, n_halfedges+5)
        new_halfedge_d = Halfedge(None, None, None, halfedge_f.vertex, None, n_halfedges+6)
        new_halfedge_dt = Halfedge(None, None, None, new_vertex.index, None, n_halfedges+7)
        new_vertex.halfedge = n_halfedges

        # Update the current halfedges to point to the new halfedges
        new_halfedge_a.next = new_halfedge_ct.index
        new_halfedge_ct.next = halfedge_c.index
        halfedge_c.next = new_halfedge_a.index

        new_halfedge_b.next = halfedge_b.index
        halfedge_b.next = new_halfedge_c.index
        new_halfedge_c.next = new_halfedge_b.index

        new_halfedge_at.next = halfedge_e.index
        halfedge_e.next = new_halfedge_d.index
        new_halfedge_d.next = new_halfedge_at.index
        
        new_halfedge_bt.next = new_halfedge_dt.index
        new_halfedge_dt.next = halfedge_f.index
        halfedge_f.next = new_halfedge_bt.index
        
        new_halfedge_a.prev = halfedge_c.index
        new_halfedge_ct.prev = new_halfedge_a.index
        halfedge_c.prev = new_halfedge_ct.index

        new_halfedge_b.prev = new_halfedge_c.index
        new_halfedge_c.prev = halfedge_b.index
        halfedge_b.prev = new_halfedge_b.index

        new_halfedge_at.prev = new_halfedge_d.index
        new_halfedge_d.prev = halfedge_e.index
        halfedge_e.prev = new_halfedge_at.index
        
        new_halfedge_bt.prev = halfedge_f.index
        halfedge_f.prev = new_halfedge_dt.index
        new_halfedge_dt.prev = new_halfedge_bt.index

        new_halfedge_a.opposite = new_halfedge_at.index
        new_halfedge_at.opposite = new_halfedge_a.index
        new_halfedge_b.opposite = new_halfedge_bt.index
        new_halfedge_bt.opposite = new_halfedge_b.index
        new_halfedge_c.opposite = new_halfedge_ct.index
        new_halfedge_ct.opposite = new_halfedge_c.index
        new_halfedge_d.opposite = new_halfedge_dt.index
        new_halfedge_dt.opposite = new_halfedge_d.index

        # Step 3: Create new faces
        new_facet_1 = Facet(halfedge_b.vertex, halfedge_c.vertex, new_vertex.index, len(self.facets), new_halfedge_b)
        new_facet_2 = Facet(halfedge_c.vertex, halfedge_a.vertex, new_vertex.index, len(self.facets) +1, new_halfedge_a)
        new_facet_3 = Facet(halfedge_e.vertex, halfedge_f.vertex, new_vertex.index, len(self.facets)+2, new_halfedge_d)
        new_facet_4 = Facet(halfedge_f.vertex, halfedge_d.vertex, new_vertex.index, len(self.facets)+3, halfedge_f)

        # Set the halfedges for the new faces
        act_facet1 = self.facets[halfedge_a.facet]
        act_facet2 = self.facets[halfedge_d.facet]
        halfedge_a.deleted = True
        halfedge_d.deleted = True
        act_facet1.deleted = True
        act_facet2.deleted = True
        new_halfedge_b.facet = new_facet_1.index
        halfedge_b.facet = new_facet_1.index
        new_halfedge_c.facet = new_facet_1.index

        halfedge_c.facet = new_facet_2.index
        new_halfedge_a.facet = new_facet_2.index
        new_halfedge_ct.facet = new_facet_2.index
        
        halfedge_e.facet = new_facet_3.index
        new_halfedge_d.facet = new_facet_3.index
        new_halfedge_at.facet = new_facet_3.index
        
        halfedge_f.facet = new_facet_4.index
        new_halfedge_dt.facet = new_facet_4.index
        new_halfedge_bt.facet = new_facet_4.index

        # facets half edges
        new_facet_1.halfedge = halfedge_b.index
        new_facet_2.halfedge = halfedge_c.index
        new_facet_3.halfedge = halfedge_e.index
        new_facet_4.halfedge = halfedge_f.index

        # Step 4: Add the new vertex and halfedges to the mesh
        self.halfedges.extend([new_halfedge_a, new_halfedge_at, new_halfedge_b, new_halfedge_bt, new_halfedge_c, new_halfedge_ct, new_halfedge_d, new_halfedge_dt])
        self.facets.extend([new_facet_1, new_facet_2, new_facet_3, new_facet_4])

        # Step 5: Ensure the Delaunay condition holds
        self.flip_edges_if_needed(halfedge_b)
        self.flip_edges_if_needed(halfedge_c)
        self.flip_edges_if_needed(halfedge_e)
        self.flip_edges_if_needed(halfedge_f)

    def locate_triangle(self, vertex):
        """
        Locate the triangle that contains the given vertex by starting with a random halfedge
        and using the orientation-based search approach.
        """
        # Step 1: Start with a random halfedge
        start_halfedge = random.choice(self.halfedges)
        # print(start_halfedge.index, start_halfedge.opposite)
        current_halfedge = start_halfedge
        # i = 0
        while True:
            # print(i, current_halfedge.index)
            # print(i, current_halfedge.facet)
            # i += 1
            # Get the triangle (facet) associated with this halfedge
            # facet = self.facets[current_halfedge.facet]
            # print("facet ", facet.index)
            
            # Check if the point is inside the current facet
            # if self.is_point_in_triangle(vertex, facet):
            #     return current_halfedge

            # Check orientation with respect to the current halfedge
            orientation = self.point_orientation(vertex, current_halfedge)
            
            if orientation == 0 and self.on_half_edge(vertex, self.vertices[current_halfedge.vertex], self.vertices[self.halfedges[current_halfedge.opposite].vertex]):
                # Point is exactly on this halfedge, return the current halfedge
                return current_halfedge
            elif orientation == -1:
                # Move to the opposite halfedge and repeat
                current_halfedge = self.halfedges[current_halfedge.opposite]
            else:
                # Check next halfedge and its next to the current facet
                next_halfedge = self.halfedges[current_halfedge.next]
                # print(next_halfedge.index, next_halfedge.opposite)
                next_orientation = self.point_orientation(vertex, next_halfedge)

                if next_orientation == 0 and self.on_half_edge(vertex, self.vertices[next_halfedge.vertex], self.vertices[self.halfedges[next_halfedge.opposite].vertex]):
                    return next_halfedge
                elif next_orientation == -1:
                    current_halfedge = self.halfedges[next_halfedge.opposite]
                else:
                    # If neither, move to the next of next halfedge
                    current_halfedge = self.halfedges[next_halfedge.next]
                    next_orientation = self.point_orientation(vertex, current_halfedge)
                    if next_orientation == 0:
                        return current_halfedge
                    elif next_orientation == -1:
                        current_halfedge = self.halfedges[current_halfedge.opposite]
                    else: 
                        return current_halfedge
                
    def flip_edges_if_needed(self, halfedge, for_restriction=False):
        """
        Flip edges to ensure the Delaunay condition is maintained.
        """
        # Verifica si ambos halfedges tienen triángulos asociados
        if halfedge.facet is None or halfedge.opposite is None:
            return  # No hay triángulo que revisar, no se puede hacer flip
        
       # Obtener el halfedge opuesto y los triángulos involucrados
        he_opposite = self.halfedges[halfedge.opposite]
        

        # Vértices de los triángulos
        v1 = self.vertices[halfedge.vertex]
        v2 = self.vertices[self.halfedges[halfedge.next].vertex]
        v3 = self.vertices[self.halfedges[halfedge.prev].vertex]  # Vértice opuesto del triángulo vecino

        # Vértice opuesto del triángulo vecino
        v_opposite = self.vertices[self.halfedges[he_opposite.prev].vertex]

        # Revisar si el vértice opuesto está dentro del circuncírculo del triángulo de 'halfedge'
        if is_point_in_circumcircle(v_opposite, v1, v2, v3):
            # No se cumple la condición de Delaunay, entonces hacemos flip
            self.flip_edge(halfedge, for_restriction)

    def flip_edge(self, halfedge, for_restriction):
        """
        Realiza un flip del halfedge dado.
        """
        if halfedge.is_restricted:
            return  # No se puede hacer flip a un halfedge restringido
        # Actualizar las referencias para los nuevos halfedges generados por el flip
        # Reasignar vértices, next, prev y opposite en función del flip

        # Nota: Este paso puede implicar reordenar las referencias en el halfedge, las
        # caras asociadas (facets) y sus halfedges.
        he_opposite = self.halfedges[halfedge.opposite]

        # Halfedges alrededor de los triángulos involucrados
        next_1 = self.halfedges[halfedge.next]
        prev_1 = self.halfedges[halfedge.prev]

        next_2 = self.halfedges[he_opposite.next]
        prev_2 = self.halfedges[he_opposite.prev]

        halfedge.vertex = prev_2.vertex
        he_opposite.vertex = prev_1.vertex 

        halfedge.next = prev_1.index
        he_opposite.next = prev_2.index
        prev_1.next = next_2.index
        next_2.next = halfedge.index
        prev_2.next = next_1.index
        next_1.next = he_opposite.index
        
        halfedge.prev = next_2.index
        he_opposite.prev = next_1.index
        prev_1.prev = halfedge.index
        next_2.prev = prev_1.index
        prev_2.prev = he_opposite.index
        next_1.prev = prev_2.index

        facet_1 = self.facets[halfedge.facet]
        facet_2 = self.facets[he_opposite.facet]

        prev_1.facet = facet_1.index
        next_2.facet = facet_1.index
        prev_2.facet = facet_2.index
        next_1.facet = facet_2.index
    
        facet_1.a = halfedge.vertex
        facet_1.b = prev_1.vertex
        facet_1.c = next_2.vertex
        facet_1.halfedge = halfedge.index
        
        facet_2.a = he_opposite.vertex
        facet_2.b = prev_2.vertex
        facet_2.c = next_1.vertex
        facet_2.halfedge = he_opposite.index

        # Actualizar triángulos, halfedges y su conexión
        # Actualizar los nuevos triángulos generados

        # ¡No olvides reasignar los 'opposites' después del flip!
        if not for_restriction:
            self.flip_edges_if_needed(prev_2)
            self.flip_edges_if_needed(next_2)

    def is_point_in_triangle(self, vertex, facet):
        """
        Determine if a vertex lies within the given triangle (facet).
        """
        # You could use a method like barycentric coordinates or cross-product tests
        hf1 = self.halfedges[facet.halfedge]
        hf2 = self.halfedges[hf1.next]
        hf3 = self.halfedges[hf2.next]

        return self.point_orientation(vertex, hf1) == 1 and self.point_orientation(vertex, hf2) == 1 and self.point_orientation(vertex, hf3) == 1 
        
    def point_orientation(self, vertex, halfedge):
        """
        Determine the orientation of the point with respect to the given halfedge.
        Returns "left", "right", or "on_segment".
        """
        # Use vector cross product or determinant method to determine orientation
        p0 = self.vertices[halfedge.vertex]  # start point of halfedge
        p1 = self.vertices[self.halfedges[halfedge.next].vertex]  # end point of halfedge
        p = vertex  # new point to check

        # Compute cross product of vectors p0p1 and p0p
        # cp = (p1.x - p0.x) * (p.y - p0.y) - (p1.y - p0.y) * (p.x - p0.x)
        cp = cross_product(p0, p1, p)
        # print("p0 ", p0.x, p0.y)
        # print("p1 ", p1.x, p1.y)
        # print("p ", p.x, p.y)
        # print("cp ", cp)
        return cp


    # def on_half_edge(self, v, halfedge):
    #     he_opposite = self.halfedges[halfedge.opposite]
    #     v0 = self.vertices[halfedge.vertex]
    #     v1 = self.vertices[he_opposite.vertex]

    #     if v0.x < v1.x:
    #         inx_1 = v0.x < v.x < v1.x 
    #     elif v0.x > v1.x:
    #         inx_1 = v1.x < v.x < v0.x 
    #     else:
    #         inx_1 = v1.x == v.x
        
    #     if v0.y < v1.y:
    #         iny_1 = v0.y < v.y < v1.y 
    #     elif v0.y > v1.y:
    #         iny_1 = v1.y < v.y < v0.y 
    #     else:
    #         iny_1 = v1.y == v.y
    #     return inx_1 and iny_1
    
    def on_half_edge(self, v, v0, v1):

        if v0.x < v1.x:
            inx_1 = v0.x < v.x < v1.x 
        elif v0.x > v1.x:
            inx_1 = v1.x < v.x < v0.x 
        else:
            inx_1 = v1.x == v.x
        
        if v0.y < v1.y:
            iny_1 = v0.y < v.y < v1.y 
        elif v0.y > v1.y:
            iny_1 = v1.y < v.y < v0.y 
        else:
            iny_1 = v1.y == v.y
        return inx_1 and iny_1
    
    def edges_intersect(self, v1, v2, hf):
        p1 = self.vertices[hf.vertex]
        p2 = self.vertices[self.halfedges[hf.opposite].vertex]

        # Verificar la orientación de los puntos
        d1 = cross_product(v1, v2, p1)
        d2 = cross_product(v1, v2, p2)
        d3 = cross_product(p1, p2, v1)
        d4 = cross_product(p1, p2, v2)

        # Caso especial: puntos colineales
        if d1 == 0 and self.on_half_edge(p1, v1, v2):
            return False  # p1 está sobre el segmento v1-v2
        if d2 == 0 and self.on_half_edge(p2, v1, v2):
            return False  # p2 está sobre el segmento v1-v2

        # Caso general: p1 y p2 están en lados opuestos de v1-v2, y viceversa
        if d1 * d2 < 0 and d3 * d4 < 0:
            return True
        
        # Si no se cumple ninguno de los casos anteriores, no hay intersección
        return False

    def remove_border_vertex(self, vertex_index):
        for he in self.halfedges:
            if he.vertex == vertex_index:
                he.deleted = True
                if he.opposite != None:
                    self.halfedges[he.opposite].deleted = True
            if self.halfedges[he.prev].vertex == vertex_index:
                self.halfedges[he.prev].deleted = True
            # self.fix_border(he, vertex_index)

    # def fix_border(self, halfedge, vertex_index):
    #     if halfedge.vertex == vertex_index and halfedge.opposite != None:
    #         he_opposite = self.halfedges[halfedge.opposite]

    #         v1 = self.vertices[self.halfedges[he_opposite.prev].vertex]
    #         v2 = self.vertices[he_opposite.vertex]
    #         v3 = self.vertices[self.halfedges[halfedge.prev].vertex]

    #         cp = cross_product(v1, v2, v3)

    #         if cp == 1:
    #             new_face = Facet(v1.index, v2.index, v3.index, self.faces_count(), halfedge.next)
    #             self.facets.append(new_face)
    #             new_halfedge = Halfedge(he_opposite.prev, None, halfedge.next, self.halfedges[halfedge.prev].vertex, new_face.index, self.half_edges_count())
    #             self.halfedges.append(new_halfedge)
    #             self.halfedges[halfedge.next].next = new_halfedge.index
    #             self.halfedges[halfedge.next].prev = self.halfedges[halfedge.opposite].prev
    #             self.halfedges[halfedge.next].facet = new_face.index
    #             self.halfedges[self.halfedges[halfedge.opposite].prev].next = halfedge.next
    #             self.halfedges[self.halfedges[halfedge.opposite].prev].prev = new_halfedge.index
    #             self.halfedges[self.halfedges[halfedge.opposite].prev].facet = new_face.index

    def __eq__(self, other):
        return (isinstance(other, type(self)) and 
            (self.vertices, self.halfedges, self.facets) ==
            (other.vertices, other.halfedges, other.facets))

    def __hash__(self):
        return (hash(str(self.vertices)) ^ hash(str(self.halfedges)) ^ hash(str(self.facets)) ^ 
            hash((str(self.vertices), str(self.halfedges), str(self.facets))))

    

    

    
    


