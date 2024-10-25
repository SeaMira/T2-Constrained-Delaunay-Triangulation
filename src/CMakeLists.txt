add_library(Triangulation STATIC
    "Mesh.h"
    "Vertex.h"
    "Facet.h"
    "HalfEdge.h"
    "shader_m.h"
    "camera3.h"
    "camera3.cpp"
)

set_property(TARGET Triangulation PROPERTY CXX_STANDARD 20)
