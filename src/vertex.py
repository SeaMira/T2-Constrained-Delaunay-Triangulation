class Vertex:

    def __init__(self, x=0, y=0, index=None, halfedge=None):
        """Create a vertex with given index at given point.

        x        - x-coordinate of the point
        y        - y-coordinate of the point
        z        - z-coordinate of the point
        index    - integer index of this vertex
        halfedge - a halfedge that points to the vertex
        """

        self.x = x
        self.y = y
        # self.z = z

        self.index = index

        self.halfedge = halfedge
        self.deleted = False

    def __eq__(x, y):
        return x.__key() == y.__key() and type(x) == type(y)

    def __key(self):
        return (self.x, self.y, self.index)

    def __hash__(self):
        return hash(self.__key())

    def get_vertex(self):
        return [self.x, self.y]