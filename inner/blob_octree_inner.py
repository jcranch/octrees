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

from octree_inner import *


class BlobTree(Tree):

    pass


class BlobEmpty(BlobTree, Empty):
    
    def extent(self):
        return None

BlobTree.empty = BlobEmpty



class BlobSingleton(BlobTree, Singleton):

    def extent(self):
        return self.data[0]

BlobTree.singleton = BlobSingleton



class BlobNode(BlobTree, Node):

    def __init__(self, content=None):
        Node.__init__(self, content)

        l = [a.extent() for a in self.children_no_bounds()]
        l = [a for a in l if a is not None]
        if len(l) == 0:
            e = (None,None,None,None,None,None)
        else:
            e = (min(a[0] for a in l),
                 max(a[1] for a in l),
                 min(a[2] for a in l),
                 max(a[3] for a in l),
                 min(a[4] for a in l),
                 max(a[5] for a in l))
        self.cached_extent = e

    def extent(self):
        return self.cached_extent

BlobTree.node = BlobNode
