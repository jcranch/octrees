"""
Unit testing for the octrees library

(C) James Cranch 2013-2014
"""

from unittest import TestCase
from math import sin

from octrees import BlobOctree
from ..geometry import *


class BlobTests(TestCase):

    def setUp(self):
        self.o = BlobOctree(((-1.0,1.0),(-1.0,1.0),(-1.0,1.0)))

        self.coords = [(sin(0.1*t), sin(0.2*t), sin(0.3*t)) for t in xrange(50)]
        m = 0.03
        self.peturbations = [(m*(1+sin(t + 3.0)), m*(1+sin(t + 4.0)), m*(1+sin(t + 5.0)), m*(1+sin(t + 6.0)), m*(1+sin(t + 7.0)), m*(1+sin(t + 8.0))) for t in xrange(50)]
        self.extents = [(x-a,x+d,y-b,y+e,z-c,z+f) for ((x,y,z),(a,b,c,d,e,f)) in zip(self.coords,self.peturbations)]

        self.o.extend(zip(self.coords, self.extents, xrange(50)))

                        
    def test_basic(self):
        self.assertEqual(len(self.o), 50)
        self.assertEqual(set(self.o), set(zip(self.coords,zip(self.extents,xrange(50)))))


