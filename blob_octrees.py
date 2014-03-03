"""
Blob octrees

(C) James Cranch 2013-2014
"""


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

    Usage:
        BlobOctree((minx,maxx),(miny,maxy),(minz,maxz))
    creates an empty blob octree with bounds as given.
    """

    def __init__(self, bounds, tree=Tree.empty()):
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
        return iter(self.tree)


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


    def extend(self,g):
        for (p,b,d) in g:
            self.insert(p,b,d)
        
