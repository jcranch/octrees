"""
Unit testing for the octrees library

(C) James Cranch 2013-2014
"""

from __future__ import division

from unittest import TestCase
from math import sin

from octrees import BlobOctree
from ..geometry import *


class BlobTests(TestCase):

    def setUp(self):
        self.o1 = BlobOctree(((-1.0,1.0),(-1.0,1.0),(-1.0,1.0)))
        self.o2 = BlobOctree(((-1.0,1.0),(-1.0,1.0),(-1.0,1.0)))

        self.coords = [(sin(0.1*t), sin(0.2*t), sin(0.3*t)) for t in xrange(100)]
        m = 0.1
        self.extents = [((x-m,x+m),(y-m,y+m),(z-m,z+m)) for (x,y,z) in self.coords]
        arguments = zip(self.coords, self.extents, xrange(100))

        self.o1.extend(arguments[:50])
        self.o2.extend(arguments[50:])
    
    def test_basic(self):
        self.assertEqual(len(self.o1), 50)
        self.assertEqual(set(self.o1), set(zip(self.coords[:50],self.extents[:50],xrange(50))))
        self.assertEqual(len(self.o2), 50)
        self.assertEqual(set(self.o2), set(zip(self.coords[50:],self.extents[50:],xrange(50,100))))

    def test_intersect_with_box(self):
        b1 = ((-0.5,0.5),(-0.2,0.8),(-0.7,0.3))
        s1 = set(self.o1.intersect_with_box(b1))
        s2 = set(self.o1.intersection_with_box(b1))
        s3 = set((p,b,d) for (p,b,d) in self.o1 if not boxes_disjoint(b,b1))
        self.assertEqual(s1,s3)
        self.assertEqual(s2,s3)

    def test_possible_overlaps(self):
        s1 = set((x[2],y[2]) for (x,y) in self.o1.possible_overlaps(self.o2))

        d2 = dict(self.o1.by_possible_overlap(self.o2))

        s2 = set((x[2],y[2]) for (x,l) in d2.iteritems() for y in l)

        s3 = set((x[2],y[2]) for x in self.o1 for y in self.o2.intersect_with_box(x[1]))

        s0 = set((x[2],y[2]) for x in self.o1 for y in self.o2 if not boxes_disjoint(x[1],y[1]))

        self.assertEqual(s1,s0)
        self.assertEqual(s2,s0)
        self.assertEqual(s3,s0)
