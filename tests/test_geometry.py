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

import random
from unittest import TestCase

from octrees.geometry import *


class GeometryTests(TestCase):

    def setUp(self):
        random.seed("vatican cameos")

    def random_point(self, n, a, b):
        return (a*random.randint(1, n)+b,
                a*random.randint(1, n)+b,
                a*random.randint(1, n)+b)

    def random_interval(self, n, a, b):
        x = a*random.randint(1, n)+b
        y = x
        while y == x:
            y = a*random.randint(1, n)+b
        return (min(x, y), max(x, y))

    def random_box(self, n, a, b):
        return (self.random_interval(n, a, b),
                self.random_interval(n, a, b),
                self.random_interval(n, a, b))

    def test_point_against_box(self):
        for i in range(10):
            b = self.random_box(100, 2, 0)

            for j in range(10):
                p = self.random_point(100, 2, 1)

                d = max(euclidean_point_point(p, v) for v in vertices(b))
                self.assertEqual(euclidean_point_box_max(p, b), d)

    def test_box_against_box(self):
        for i in range(10):
            a = self.random_box(100, 2, 0)
            b = self.random_box(100, 2, 1)

            d2 = euclidean_box_box_max(a, b)
            d1 = max(euclidean_point_box_max(u, b) for u in vertices(a))
            d0 = max(euclidean_point_point(u, v)
                     for u in vertices(a)
                     for v in vertices(b))

            self.assertEqual(d1, d0)
            self.assertEqual(d2, d0)

    def test_line_segment_against_box1(self):
        b = ((-0.0831860995156494, 0.11681390048435061),
             (-0.06637695277886153, 0.1336230472211385),
             (-0.04957731219318878, 0.15042268780681123))
        p = (-0.5, -0.5, -0.5)
        q = (0.5, 0.5, 0.5)
        self.assertTrue(line_segment_intersects_box(p, q, b))
        self.assertTrue(line_segment_intersects_box(q, p, b))

    def test_line_segment_against_box2(self):
        b = ((0.09866933079506121, 0.2986693307950612),
             (0.2894183423086505, 0.48941834230865056),
             (0.4646424733950354, 0.6646424733950353))
        p = (-0.5, -0.5, -0.5)
        q = (0.5, 0.5, 0.5)
        self.assertFalse(line_segment_intersects_box(p, q, b))
        self.assertFalse(line_segment_intersects_box(q, p, b))

    def test_box_intersects_plane(self):
        b = ((0.09866933079506121, 0.2986693307950612),
             (0.2894183423086505, 0.48941834230865056),
             (0.4646424733950354, 0.6646424733950353))
        f = lambda p: p[0]-0.25
        self.assertTrue(box_intersects_plane(b, f))
