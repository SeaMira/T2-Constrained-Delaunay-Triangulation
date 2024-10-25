add_library(Triangulation STATIC
    "Mesh.h"
    "Vertex.h"
    "Facet.h"
    "HalfEdge.h"
)

set_property(TARGET Triangulation PROPERTY CXX_STANDARD 20)
