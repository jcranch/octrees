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
Unit testing for the octrees library

(C) James Cranch 2013--2021
"""

from unittest import TestCase
from math import sin

from octrees.blob_octrees import BlobOctree
from octrees.geometry import *


class BlobTests(TestCase):

    def setUp(self):
        self.o1 = BlobOctree(((-1.0, 1.0), (-1.0, 1.0), (-1.0, 1.0)))
        self.o2 = BlobOctree(((-1.0, 1.0), (-1.0, 1.0), (-1.0, 1.0)))

        self.coords = [(sin(0.1*t), sin(0.2*t), sin(0.3*t))
                       for t in range(100)]
        m = 0.1
        self.extents = [((x-m, x+m), (y-m, y+m), (z-m, z+m))
                        for (x, y, z) in self.coords]
        arguments = list(zip(self.coords, self.extents, range(100)))

        self.o1.extend(arguments[:50])
        self.o2.extend(arguments[50:])

    def test_basic(self):
        self.assertEqual(len(self.o1), 50)
        self.assertEqual(set(self.o1),
                         set(zip(self.coords[:50],
                                 self.extents[:50],
                                 range(50))))
        self.assertEqual(len(self.o2), 50)
        self.assertEqual(set(self.o2),
                         set(zip(self.coords[50:],
                                 self.extents[50:],
                                 range(50, 100))))

    def test_intersect_with_box(self):
        b1 = ((-0.5, 0.5), (-0.2, 0.8), (-0.7, 0.3))
        s1 = set(self.o1.intersect_with_box(b1))
        s2 = set(self.o1.intersection_with_box(b1))
        s3 = set((p, b, d)
                 for (p, b, d) in self.o1
                 if not boxes_disjoint(b, b1))
        self.assertEqual(s1, s3)
        self.assertEqual(s2, s3)

    def test_possible_overlaps(self):
        s1 = set((x[2], y[2]) for (x, y) in self.o1.possible_overlaps(self.o2))

        d2 = dict(self.o1.by_possible_overlap(self.o2))

        s2 = set((x[2], y[2]) for (x, l) in d2.items() for y in l)

        s3 = set((x[2], y[2])
                 for x in self.o1
                 for y in self.o2.intersect_with_box(x[1]))

        s0 = set((x[2], y[2])
                 for x in self.o1
                 for y in self.o2
                 if not boxes_disjoint(x[1], y[1]))

        self.assertEqual(s1, s0)
        self.assertEqual(s2, s0)
        self.assertEqual(s3, s0)

    def test_intersect_with_line(self):
        for xi in range(-8, 8, 2):
            x = xi/10
            for yi in range(-8, 8, 2):
                y = yi/10
                for zi in range(-8, 8, 2):
                    z = zi/10

                    def decent(t):
                        ((minx, maxx), (miny, maxy), (minz, maxz)) = t
                        return maxx > x and miny < y < maxy and minz < z < maxz

                    s0 = set(self.o1.intersect_with_line((x, y, z), (1, 0, 0)))
                    s1 = set(t for t in self.o1 if decent(t[1]))

                    self.assertEqual(s0, s1)

    def test_intersect_with_line_segment(self):
        s0 = set(self.o1.intersect_with_line_segment((-0.5, -0.5, -0.5),
                                                     (0.5, 0.5, 0.5)))
        s1 = set()
        for t in zip(self.coords, self.extents, range(50)):
            (p, b, n) = t
            for i in range(-500, 501):
                x = (i/1000.0, i/1000.0, i/1000.0)
                if point_in_box(x, b):
                    s1.add(t)
                    break
        self.assertEqual(s0, s1)

    def test_intersect_with_plane(self):
        for d in [0]:
            fn = lambda p: p[d]-0.25

            s0 = set(self.o1.intersect_with_plane(fn))
            s1 = set()
            for t in zip(self.coords, self.extents, range(50)):
                (_, b, _) = t
                if b[d][0] <= 0.25 <= b[d][1]:
                    s1.add(t)
            self.assertEqual(s0, s1)
