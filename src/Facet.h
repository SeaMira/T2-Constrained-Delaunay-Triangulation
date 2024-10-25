// Facet.h
#ifndef FACET_H
#define FACET_H

#include <memory>
#include "Vertex.h"
#include "HalfEdge.h"

// Forward declaration de HalfEdge
class HalfEdge;

class Facet {
public:
    std::shared_ptr<Vertex> a, b, c;
    std::shared_ptr<HalfEdge> halfedge;
    int index;
    bool deleted;

    Facet(const std::shared_ptr<Vertex>& v1, const std::shared_ptr<Vertex>& v2, const std::shared_ptr<Vertex>& v3, int index = -1)
        : a(v1), b(v2), c(v3), index(index), deleted(false) {}
};

#endif  // FACET_H