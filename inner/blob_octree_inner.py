#    Octrees in Python
#    Copyright (C) 2013--14  James Cranch
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

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

from ..geometry import *
from .octree_inner import *


class BlobTree(Tree):

    def extent(self):
        """
        Returns the bounds ((minx, maxx), (miny, maxy), (minz, maxz)).
        """
        raise NotImplementedError

    def intersection_with_box(self, b):

        def point_fn(e):
            return not boxes_disjoint(e, b)

        def box_fn(e):
            if boxes_disjoint(e, b):
                return False
            if box_contains(e, b):
                return True
            return None

        return self.subset_by_extent(point_fn, box_fn)

    def intersect_with_box(self, b):
        """
        Yield regions whose extents overlap with b.
        """
        def point_fn(e):
            return not boxes_disjoint(e, b)

        def box_fn(e):
            if boxes_disjoint(e, b):
                return False
            if box_contains(e, b):
                return True
            return None

        for t in self.iter_by_extent(point_fn, box_fn):
            yield t

    def intersect_with_line(self, a, v, positive=True):
        """
        Yields regions which overlap with the line a+rv. If "positive"
        is true, then r must be positive (so in fact, you are
        intersecting with a halfline).
        """

        def point_fn(e):
            if positive:
                return halfline_intersects_box(a, v, e)
            else:
                return line_intersects_box(a, v, e)

        def box_fn(e):
            return (point_fn(e) and None)

        for t in self.iter_by_extent(point_fn, box_fn):
            yield t

    def intersect_with_line_segment(self, a, b):
        """
        Yields regions which overlap with the line between a and b.
        """

        def point_fn(e):
            return line_segment_intersects_box(a, b, e)

        def box_fn(e):
            return (point_fn(e) and None)

        for t in self.iter_by_extent(point_fn, box_fn):
            yield t

    def intersect_with_plane(self, f):
        """
        Yields regions whose extents have at least one corner p with
        f(p)>=0 and at least one corner q with f(q)<=0. In case f is a
        linear functional (the intended use), this gives regions whose
        extents lie on a plane.
        """

        def point_fn(e):
            return box_intersects_plane(e, f)

        def box_fn(e):
            return box_intersects_plane(e, f) and None

        return self.iter_by_extent(point_fn, box_fn)


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

    def possible_overlaps(self, other):
        return
        yield

    def by_possible_overlap(self, other):
        return
        yield

    def debug_description(self, indent):
        print("  "*indent + "Empty")

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

    def possible_overlaps(self, other):
        t1 = self.data_triple()
        for t2 in other.intersect_with_box(self.extent()):
            yield (t1, t2)

    def by_possible_overlap(self, other):
        e = self.data[0]
        yield (self.data_triple(), list(other.intersect_with_box(e)))

    def debug_description(self, indent):
        s = "Singleton at %s with bounds %s and data %s" % (
            self.data_triple())
        print("  "*indent + s)

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

    def subset_by_extent(self, point_fn, box_fn):
        a = box_fn(self.extent())
        if a is None:
            return self.smartnode([t.subset_by_extent(point_fn, box_fn)
                                   for t in self.children_no_bounds()])
        elif a:
            return self
        else:
            return self.empty()

    def iter_by_extent(self, point_fn, box_fn):
        a = box_fn(self.extent())
        if a is None:
            for t in self.children_no_bounds():
                for r in t.iter_by_extent(point_fn, box_fn):
                    yield r
        elif a:
            for (p, (b, d)) in self:
                yield (p, b, d)

    def reroot(self):
        """
        Discards unnecessary tree data at the root, at the cost of
        losing track of anything we knew about bounds.

        Useful in a couple of algorithms.
        """
        l = list(self.children_no_bounds())
        s = sum(isinstance(x, BlobEmpty) for x in l)
        if s == 7:
            for x in l:
                if not isinstance(x, BlobEmpty):
                    return x.reroot()
        else:
            return self

    def possible_overlaps(self, other):
        o = other.intersection_with_box(self.extent()).reroot()
        for s in self.children_no_bounds():
            for x in s.possible_overlaps(o):
                yield x

    def by_possible_overlap(self, other):
        for s in self.children_no_bounds():
            e = s.extent()
            if e is not None:
                a = other.intersection_with_box(e).reroot()
                for x in s.by_possible_overlap(a):
                    yield x

    def debug_description(self, indent):
        print ("  "*indent + "Node with extent %s:" % (self.extent(),))
        for s in self.children_no_bounds():
            s.debug_description(indent+1)

BlobTree.node = BlobNode
