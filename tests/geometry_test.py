"""
Unit testing for the octrees library

(C) James Cranch 2013-2014
"""

import random
from unittest import TestCase

from ..geometry import *


class GeometryTests(TestCase):

    def setUp(self):
        random.seed("vatican cameos")

    def random_point(self,n,a,b):
        return (a*random.randint(1,n)+b, a*random.randint(1,n)+b, a*random.randint(1,n)+b)

    def random_interval(self,n,a,b):
        x = a*random.randint(1,n)+b
        y = x
        while y == x:
            y = a*random.randint(1,n)+b
        return (min(x,y),max(x,y))

    def random_box(self,n,a,b):
        return (self.random_interval(n,a,b),self.random_interval(n,a,b),self.random_interval(n,a,b))

    def test_point_against_box(self):
        for i in xrange(10):
            b = self.random_box(100,2,0)

            for j in xrange(10):
                p = self.random_point(100,2,1)

                d = max(euclidean_point_point(p,v) for v in vertices(b))
                self.assertEqual(euclidean_point_box_max(p,b), d)

    def test_box_against_box(self):
        for i in xrange(10):
            a = self.random_box(100,2,0)
            b = self.random_box(100,2,1)

            d2 = euclidean_box_box_max(a,b)
            d1 = max(euclidean_point_box_max(u,b) for u in vertices(a))
            d0 = max(euclidean_point_point(u,v) for u in vertices(a) for v in vertices(b))

            self.assertEqual(d1,d0)
            self.assertEqual(d2,d0)
