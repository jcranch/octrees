#    Octrees in Python
#    Copyright (C) 2013--2021  James Cranch
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
The core functionality: a purely functional implementation. We have
this two-layer setup so that octree nodes do not have to store their
own bounds.

Also, people used to python expect mutable data structures; mutability
is most easily provided using a wrapper.

The user should probably not ever want to import or use this code
directly.

(C) James Cranch 2013--2021
"""

from functools import reduce
import heapq

from octrees.geometry import *
from octrees.inner.misc import pivot


class Tree(object):

    def smartnode(self, data):
        """
        Assembles the given octants into a node.
        """

        if len(data) != 8:
            (((a, b), (c, d)), ((e, f), (g, h))) = data
            data = [a, b, c, d, e, f, g, h]
        singleton = None
        for x in data:
            if isinstance(x, Node):
                return self.node(data)
            elif isinstance(x, Singleton):
                if singleton is not None:
                    return self.node(data)
                else:
                    singleton = x
        if singleton is not None:
            return singleton
        else:
            return self.empty()


class Empty(Tree):

    def __init__(self):
        pass

    def __iter__(self):
        return
        yield

    def __len__(self):
        return 0

    def __eq__(self, other):
        return isinstance(other, Empty)

    def __hash__(self):
        return hash((self.empty,))

    def get(self, bounds, coords, default):
        return default

    def insert(self, bounds, coords, data):
        return self.singleton(coords, data)

    def update(self, bounds, coords, data, replace=True):
        return self.singleton(coords, data)

    def remove(self, bounds, coords):
        raise KeyError("Removing non-existent point")

    def subset(self, bounds, point_fn, box_fn):
        return self

    def enqueue(self, heap, bounds, pointscore, boxscore):
        pass

    def union(self, other, bounds, swapped=False):
        return other

    def rebound(self, oldbounds, newbounds):
        return self

    def deform(self, oldbounds, newbounds, point_fn, box_fn):
        return self

Tree.empty = Empty


class Singleton(Tree):

    def __init__(self, coords, data):
        self.coords = coords
        self.data = data

    def __len__(self):
        return 1

    def __iter__(self):
        yield (self.coords, self.data)

    def __eq__(self, other):
        return (isinstance(other, Singleton)
                and self.coords == other.coords
                and self.data == other.data)

    def __hash__(self):
        return hash((self.singleton, coords, data))

    def get(self, bounds, coords, default):
        if self.coords == coords:
            return self.data
        else:
            return default

    def insert(self, bounds, coords, data):
        if self.coords == coords:
            raise KeyError("Key (%s,%s,%s) already present" % (self.coords))
        else:
            return self.node().insert(bounds, self.coords,
                                      self.data).insert(bounds, coords, data)

    def update(self, bounds, coords, data, replace=True):
        if self.coords == coords:
            if replace:
                return self.singleton(coords, data)
            else:
                return self
        else:
            return self.node().insert(bounds, self.coords,
                                      self.data).insert(bounds, coords, data)

    def remove(self, bounds, coords):
        if self.coords == coords:
            return self.empty()
        else:
            raise KeyError("Removing non-existent point")

    def subset(self, bounds, point_fn, box_fn):
        if point_fn(self.coords):
            return self
        else:
            return self.empty()

    def enqueue(self, heap, bounds, pointscore, boxscore):
        s = pointscore(self.coords)
        if s is not None:
            heapq.heappush(heap, (s, False, self.coords, self.data))

    def union(self, other, bounds, swapped=False):
        return other.update(bounds, self.coords, self.data, replace=swapped)

    def rebound(self, oldbounds, newbounds):
        if point_in_box(self.coords, newbounds):
            return self
        else:
            return self.empty()

    def deform(self, oldbounds, newbounds, point_fn, box_fn):
        coords = point_fn(self.coords)
        if point_in_box(coords, newbounds):
            return self.singleton(coords, self.data)
        else:
            return self.empty()

Tree.singleton = Singleton


class Node(Tree):

    def __init__(self, content=None):
        """
        Takes either a generator of eight octrees, or generators of two
        nested three deep (or None for an empty octree).
        """
        if content is None:
            content = (self.empty(),)*8
        else:
            content = tuple(content)
            if len(content) == 2:
                content = tuple(x for x in b for b in a for a in content)
            if len(content) != 8:
                raise ValueError("Content in unrecognised format")
        self.content = content

    def __len__(self):
        return sum(len(x) for x in self.content)

    def __iter__(self):
        for x in self.content:
            for t in iter(x):
                yield t

    def __eq__(self, other):
        if isinstance(other, Node):
            return self.content == other.content
        else:
            return False

    def __hash__(self):
        return hash((self.node, content))

    def get(self, bounds, coords, default):
        (n, newbounds) = narrow(bounds, coords)
        return self.content[n].get(newbounds, coords, default)

    def insert(self, bounds, coords, data):
        a = list(self.content)
        (n, newbounds) = narrow(bounds, coords)
        a[n] = a[n].insert(newbounds, coords, data)
        return self.node(a)

    def update(self, bounds, coords, data, replace=True):
        a = list(self.content)
        (n, newbounds) = narrow(bounds, coords)
        a[n] = a[n].update(newbounds, coords, data, replace=replace)
        return self.node(a)

    def remove(self, bounds, coords):
        a = list(self.content)
        (n, newbounds) = narrow(bounds, coords)
        a[n] = a[n].remove(newbounds, coords)
        return self.smartnode(a)

    def children(self, bounds):
        return zip(subboxes(bounds), self.content)

    def subset(self, bounds, point_fn, box_fn):
        x = box_fn(bounds)
        if x is None:
            return self.smartnode(list(t.subset(b, point_fn, box_fn)
                                       for (b, t) in self.children(bounds)))
        elif x:
            return self
        else:
            return self.empty()

    def enqueue(self, heap, bounds, pointscore, boxscore):
        s = boxscore(bounds)
        if s is not None:
            heapq.heappush(heap, (s, True, bounds, self))

    def union(self, other, bounds, swapped=False):
        if not isinstance(other, Node):
            return other.union(self, bounds, not swapped)
        if swapped:
            return other.union(self, bounds, swapped=False)
        else:
            return self.node([x.union(y, b)
                              for (x, y, b) in zip(self.content,
                                                   other.content,
                                                   subboxes(bounds))])

    def rebound(self, oldbounds, newbounds):
        if box_contains(oldbounds, newbounds):
            return self.node([self.rebound(oldbounds, b)
                              for b in subboxes(newbounds)])
        elif boxes_disjoint(oldbounds, newbounds):
            return self.empty()
        else:
            return reduce(lambda x, y: x.union(y, newbounds),
                          (x.rebound(b, newbounds)
                           for (b, x) in self.children(oldbounds)))

    def deform(self, oldbounds, newbounds, point_fn, box_fn):
        if box_contains(oldbounds, newbounds):
            return self.node([self.deform(oldbounds, b, point_fn, box_fn)
                              for b in subboxes(newbounds)])
        elif boxes_disjoint(box_fn(oldbounds), newbounds):
            return self.empty()
        else:
            return reduce(lambda x, y: x.union(y, newbounds),
                          (x.deform(b, newbounds, point_fn, box_fn)
                           for (b, x) in self.children(oldbounds)))

Tree.node = Node


def octree_from_list_inner(bounds, l, start, stop):
    if start == stop:
        return Empty()
    elif start+1 == stop:
        (p,d) = l[start]
        return Singleton(p,d)
    else:
        (midx, midy, midz) = centroid(bounds)
        n4 = pivot(l, lambda t: t[0][0]<midx, start, stop)
        n2 = pivot(l, lambda t: t[0][1]<midy, start, n4)
        n6 = pivot(l, lambda t: t[0][1]<midy, n4, stop)
        n1 = pivot(l, lambda t: t[0][2]<midz, start, n2)
        n3 = pivot(l, lambda t: t[0][2]<midz, n2, n4)
        n5 = pivot(l, lambda t: t[0][2]<midz, n4, n6)
        n7 = pivot(l, lambda t: t[0][2]<midz, n6, stop)
        return Node([octree_from_list_inner(b, l, r, s)
                     for (b,r,s) in zip(
                             subboxes(bounds),
                             [start, n1, n2, n3, n4, n5, n6, n7],
                             [n1, n2, n3, n4, n5, n6, n7, stop])])
