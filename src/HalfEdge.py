import sys
import math
from . import config
from .alg import norm, normalize,cross_product

class Halfedge:

    def __init__(self, next=None, opposite=None, prev=None, vertex=None,
                 facet=None, index=None, is_restricted=False):
        """Create a halfedge with given index.
        """
        self.opposite = opposite
        self.next = next
        self.prev = prev
        self.vertex = vertex
        self.facet = facet
        self.index = index
        self.is_restricted = is_restricted
        self.deleted = False

    def __eq__(self, other):
        # TODO Test more
        return (self.vertex == other.vertex) and \
               (self.prev.vertex == other.prev.vertex) and \
               (self.index == other.index)

    def __hash__(self):
        return hash(self.opposite) ^ hash(self.next) ^ hash(self.prev) ^ \
                hash(self.vertex) ^ hash(self.facet) ^ hash(self.index) ^ \
                hash((self.opposite, self.next, self.prev, self.vertex,
                    self.facet, self.index))

    