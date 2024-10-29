#ifndef HALF_EDGE_H
#define HALF_EDGE_H

#include "Vertex.h"

// Forward declaration de Facet
class Facet;

class HalfEdge {
public:
    std::shared_ptr<HalfEdge> opposite;
    std::shared_ptr<HalfEdge> next;
    std::shared_ptr<HalfEdge> prev;
    std::shared_ptr<Vertex> vertex;
    std::shared_ptr<Facet> facet;
    int index;
    bool is_border = false;
    bool is_restricted = false;
    bool deleted;

    HalfEdge(int index = -1, std::shared_ptr<Vertex> vertex = nullptr)
        : index(index), vertex(vertex), deleted(false) {}

};

#endif  // HALF_EDGE_H