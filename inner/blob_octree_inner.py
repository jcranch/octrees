"""
A customised internal octree structure, designed for storing objects
with spatial extent. While each object is associated to a single
point, each node stores a box describing the extent of its contents
(which may well exceed the bounds for the associated points it will
store).

The user should probably not ever want to import or use this code
directly.

(C) James Cranch 2013-2014
"""

from __future__ import division

from octrees.geometry import *
from octree_inner import *



class BlobTree(Tree):

    def intersection_with_box(self,b):

        def point_fn(e):
            return not boxes_disjoint(e,b)

        def box_fn(e):
            if boxes_disjoint(e,b):
                return False
            if box_contains(e,b):
                return True
            return None

        return self.subset_by_extent(point_fn, box_fn)

    def intersect_with_box(self,b):
        """
        Yield regions whose extents overlap with b.
        """
        def point_fn(e):
            return not boxes_disjoint(e,b)

        def box_fn(e):
            if boxes_disjoint(e,b):
                return False
            if box_contains(e,b):
                return True
            return None

        for t in self.iter_by_extent(point_fn, box_fn):
            yield t



class BlobEmpty(BlobTree, Empty):
    
    def extent(self):
        return None

    def subset_by_extent(self, point_fn, box_fn):
        return self

    def iter_by_extent(self, point_fn, box_fn):
        return
        yield

    def reroot(self):
        return self

    def possible_overlaps(self,other):
        return
        yield

    def by_possible_overlap(self,other):
        return
        yield

    def debug_description(self,indent):
        print "  "*indent + "Empty"

BlobTree.empty = BlobEmpty



class BlobSingleton(BlobTree, Singleton):

    def data_triple(self):
        return (self.coords, self.data[0], self.data[1])

    def extent(self):
        return self.data[0]

    def subset_by_extent(self, point_fn, box_fn):
        if point_fn(self.extent()):
            return self
        else:
            return self.empty()

    def iter_by_extent(self, point_fn, box_fn):
        if point_fn(self.extent()):
            yield self.data_triple()

    def reroot(self):
        return self

    def possible_overlaps(self,other):
        t1 = self.data_triple()
        for t2 in other.intersect_with_box(self.extent()):
            yield (t1,t2)

    def by_possible_overlap(self,other):
        e = self.data[0]
        yield (self.data_triple(),list(other.intersect_with_box(e)))

    def debug_description(self,indent):
        print "  "*indent + "Singleton at %s with bounds %s and data %s"%(self.data_triple())

BlobTree.singleton = BlobSingleton



class BlobNode(BlobTree, Node):

    def __init__(self, content=None):
        Node.__init__(self, content)

        l = [a.extent() for a in self.children_no_bounds()]
        l = [a for a in l if a is not None]
        if len(l) == 0:
            e = None
        else:
            e = ((min(a[0][0] for a in l),
                  max(a[0][1] for a in l)),
                 (min(a[1][0] for a in l),
                  max(a[1][1] for a in l)),
                 (min(a[2][0] for a in l),
                  max(a[2][1] for a in l)))
        self.cached_extent = e

    def extent(self):
        return self.cached_extent

    def subset_by_extent(self,point_fn,box_fn):
        a = box_fn(self.extent())
        if a is None:
            return self.smartnode([t.subset_by_extent(point_fn,box_fn) for t in self.children_no_bounds()])
        elif a:
            return self
        else:
            return self.empty()

    def iter_by_extent(self,point_fn,box_fn):
        a = box_fn(self.extent())
        if a is None:
            for t in self.children_no_bounds():
                for r in t.iter_by_extent(point_fn, box_fn):
                    yield r
        elif a:
            for (p,(b,d)) in self:
                yield (p,b,d)

    def reroot(self):
        """
        Discards unnecessary tree data at the root, at the cost of
        losing track of anything we knew about bounds.

        Useful in a couple of algorithms.
        """
        l = list(self.children_no_bounds())
        s = sum(isinstance(x,BlobEmpty) for x in l)
        if s == 7:
            for x in l:
                if not isinstance(x,BlobEmpty):
                    return x.reroot()
        else:
            return self

    def possible_overlaps(self,other):
        o = other.intersection_with_box(self.extent()).reroot()
        for s in self.children_no_bounds():
            for x in s.possible_overlaps(o):
                yield x

    def by_possible_overlap(self,other):
        for s in self.children_no_bounds():
            e = s.extent()
            if e is not None:
                for x in s.by_possible_overlap(other.intersection_with_box(e).reroot()):
                    yield x

    def debug_description(self,indent):
        print "  "*indent + "Node with extent %s:"%(self.extent(),)
        for s in self.children_no_bounds():
            s.debug_description(indent+1)

BlobTree.node = BlobNode
