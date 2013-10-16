# A simple octree library
#
# James Cranch, 2013
#
# *add a licence*


# to do
#   points by linear functional
#   find nearby points in two octrees
#   transform by continuous function (eg matrix)


import heapq

from geometry import *
from octree_inner import *


class Octree():
    """
    Octrees: efficient data structure for data associated with points
    in 3D space.
    """

    def __init__(self, bounds, tree=Empty()):
        self.bounds = bounds
        self.tree = tree


    def check_bounds(self, p):
        if not point_in_box(p, self.bounds):
            raise KeyError("Point (%s,%s,%s) out of bounds"%p)


    def __len__(self):
        return len(self.tree)


    def __eq__(self, other):
        return self.bounds == other.bounds and self.tree == other.tree

    
    def insert(self, p, d):
        """
        Adds a point at p with value d. Raises KeyError if there is
        already a point there (unlike the "update" method).
        """
        self.check_bounds(p)
        self.tree = self.tree.insert(self.bounds, p, d)


    def update(self, p, d):
        """
        Adds a point at p with value d. Overwrites if there is already
        a point there (unlike the "insert" method).
        """
        self.check_bounds(p)
        self.tree = self.tree.update(self.bounds, p, d)


    def remove(self, p):
        """
        Removes the point at p; raises KeyError if there is not such a
        point.
        """
        self.check_bounds(p)
        self.tree = self.tree.remove(self.bounds, p)


    def extend(self, g):
        "Inserts all the points in g."
        for (p,d) in g:
            self.insert(p,d)


    def simple_union(self, other):
        """
        Return the union of two octrees with the same bounds. When
        there are points in both, one will overwrite the other (which
        of the two remain is undefined).
        """
        if self.bounds != other.bounds:
            raise ValueError("Bounds don't agree")
        return Octree(self.bounds, self.tree.union(other.tree, self.bounds))


    def rebound(self, newbounds):
        """
        New version with changed bounds, and with a tree restructured
        accordingly. Drops all points lying outside the new bounds.
        """
        return Octree(newbounds, self.tree.rebound(self.bounds, newbounds))


    def general_union(self, other):
        """
        Return the union of two octrees of arbitrary bounds. When
        there are points in both, one will overwrite the other (which
        of the two remain is undefined).
        """
        x = self
        y = other
        b = union_box(x.bounds, y.bounds)
        if b != x.bounds:
            x = x.rebound(b)
        if b != y.bounds:
            y = y.rebound(b)
        return x.simple_union(y)
        

    def by_score(self, pointscore, boxscore):
        """
        Iterates through points in some kind of geometric order: for
        example, proximity to a given point.

        Returns tuples of the form (score, coords, value).

        Arguments:

        - pointscore
            A function which associates to coordinates (x,y,z) a
            value, the "score". Lower scores will be returned
            earlier. A score of None is considered infinite: that
            point will not be returned.

        - boxscore
            A function which assigns to a box the lowest possible
            score of any point in that box. Again, a score of None is
            considered infinite: we cannot be interested in any point
            in that box.

        The algorithm maintains a heap of points and boxes in order of
        how promising they are. In particular, if only the earliest
        results are needed, not much extra processing is done.
        """
        l = []
        self.tree.enqueue(l, self.bounds, pointscore, boxscore)

        while len(l)>0:
            (score,isnode,location,stuff) = heapq.heappop(l)
            if isnode:
                for (b,t) in stuff.children(location):
                    t.enqueue(l, b, pointscore, boxscore)
            else:
                yield (score,location,stuff)


    def by_distance_from_point(self, p):
        """
        Return points in order of distance from p, in the form
        (distance, coords, value).
        """
        for t in self.by_score(lambda q: euclidean_point_point(p,q), lambda b: euclidean_point_box(p,b)):
            yield t

    
    def by_distance_from_point_rev(self, p):
        """
        Return points in order of distance from p, in the form
        (distance, coords, value), furthest first.
        """
        for (d,c,v) in self.by_score(lambda q: -euclidean_point_point(p,q), lambda b: min(-euclidean_point_point(p,q) for q in vertices(b))):
            yield (-d,c,v)
        

    def nearest_to_point(self, p):
        """
        Return the nearest point to p, in the form (distance, coords,
        value).
        """
        for t in self.by_distance_from_point(p):
            return t


    def near_point(self, p, epsilon):
        """
        Return all points within epsilon of p, in the form (distance,
        coords, value). A little faster than using
        by_distance_from_point and stopping when satisfied.
        """
        def pointscore(q):
            s = euclidean_point_point(p,q)
            if s < epsilon:
                return s
            else:
                return None
        def boxscore(b):
            s = euclidean_point_box(p,b)
            if s < epsilon:
                return s
            else:
                return None
        for t in self.by_score(pointscore, boxscore):
            yield t
    
