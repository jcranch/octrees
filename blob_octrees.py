"""
Blob octrees

(C) James Cranch 2013-2014
"""

from __future__ import division

import heapq

from geometry import *
from inner.blob_octree_inner import *


class BlobOctree():
    """
    Blob Octrees: an efficient data structure for data associated with
    regions in 3D space. Each region must be associated to a reference
    point, which must be unique, and must lie within certain bounds
    (the region need not lie within those bounds).

    It is very helpful (though not required) if the reference point is
    somewhere near that region. In practice, choosing the centroid is
    a good option.

    We demand that every region has an "extent", a box which bounds
    it.

    Usage:
        BlobOctree((minx,maxx),(miny,maxy),(minz,maxz))
    creates an empty blob octree with bounds as given.
    """

    def __init__(self, bounds, tree=BlobTree.empty()):
        self.bounds = bounds
        self.tree = tree

    
    def check_bounds(self, p):
        if not point_in_box(p, self.bounds):
            raise KeyError("Point (%s,%s,%s) out of bounds"%p)


    def __len__(self):
        return len(self.tree)


    def __eq__(self, other):
        return self.bounds == other.bounds and self.tree == other.tree


    def __iter__(self):
        for (p,(b,d)) in self.tree:
            yield (p,b,d)


    def insert(self,p,b,d):
        """
        Insert a region with reference point p, bounds b, and
        associated data d. Raises KeyError if there is already a
        region with that reference point (unlike the "update" method).
        """
        self.check_bounds(p)
        self.tree = self.tree.insert(self.bounds, p, (b,d))


    def update(self,p,b,d):
        """
        Insert a region with reference point p, bounds b, and
        associated data d. Overwrites if there is already a region
        with that reference point (unlike the "insert" method).
        """
        self.check_bounds(p)
        self.tree = self.tree.update(self.bounds, p, (b,d))


    def copy(self):
        """
        Return a copy of self.

        Since BlobOctree is just a wrapper for a pure data structure,
        this is performed in constant time.
        """
        return BlobOctree(self.bounds, self.tree)


    def extend(self,g):
        for (p,b,d) in g:
            self.insert(p,b,d)


    def intersection_with_box(self,b):
        """
        Find the sub-octree of regions whose extents overlap with b.
        """
        return BlobOctree(self.bounds, self.tree.intersection_with_box(b))


    def intersect_with_box(self,b):
        """
        Yield regions whose extents overlap with b.
        """
        for t in self.tree.intersect_with_box(b):
            yield t


    def possible_overlaps(self,other):
        """
        Yields pairs of regions whose extents overlap, one from each
        blob octree.

        Likely to be of use in writing algorithms to compute geometric
        intersections.
        """

        for t in self.tree.possible_overlaps(other.tree):
            yield t


    def by_possible_overlap(self,other):
        """
        Yields regions in self together with a list of regions from
        other whose extents overlap.

        Likely to be of use in writing algorithms to compute geometric
        differences.
        """
        for t in self.tree.by_possible_overlap(other.tree):
            yield t


    def debug_description(self):
        """
        Describes the tree structure, for debugging purposes.
        """
        print "Octree with bounds %s:"%(self.bounds,)
        self.tree.debug_description(1)
