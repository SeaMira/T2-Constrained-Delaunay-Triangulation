#ifndef VERTEX_H
#define VERTEX_H

#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>
#include <CGAL/intersections.h>
#include <vector>
#include <memory>

typedef CGAL::Exact_predicates_inexact_constructions_kernel K;
typedef K::Point_2 Point;
typedef K::Segment_2 Segment;

class Vertex {
public:
    double x, y;
    int index;
    bool deleted;
    std::shared_ptr<class HalfEdge> halfedge;

    Vertex(double x = 0, double y = 0, int index = -1)
        : x(x), y(y), index(index), deleted(false) {}

    Point to_cgal_point() const {
        return Point(x, y);
    }
};

#endif // VERTEX_H