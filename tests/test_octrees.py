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

from octrees import Octree, octree_from_list
from octrees.geometry import *


class BasicTests(TestCase):

    def setUp(self):
        self.o = Octree(((0.0, 1.0), (0.0, 1.0), (0.0, 1.0)))
        self.o.insert((0.33, 0.66, 0.99), "Point one")
        self.o.insert((0.12, 0.34, 0.56), "Point two")
        self.o.insert((0.98, 0.76, 0.54), "Point three")

    def test_size(self):
        self.assertEqual(len(self.o), 3)

    def test_thinking_outside_box(self):
        with self.assertRaises(KeyError):
            self.o.insert((2.35, 0.87, 0.56), "> maxx")
        with self.assertRaises(KeyError):
            self.o.insert((-0.43, 0.87, 0.56), "< minx")
        with self.assertRaises(KeyError):
            self.o.insert((0.35, 1.94, 0.56), "> maxy")
        with self.assertRaises(KeyError):
            self.o.insert((0.35, -0.51, 0.56), "< miny")
        with self.assertRaises(KeyError):
            self.o.insert((0.35, 0.87, 1.04), "> maxz")
        with self.assertRaises(KeyError):
            self.o.insert((0.35, 0.87, -0.35), "< minz")

    def test_update_insert(self):
        with self.assertRaises(KeyError):
            self.o.insert((0.33, 0.66, 0.99), "Point one, renewed")
        self.o.update((0.33, 0.66, 0.99), "Point one, renewed")
        self.assertEqual(len(self.o), 3)
        self.o.insert((0.98, 0.23, 0.15), "Point four")
        self.assertEqual(len(self.o), 4)


class BuilderTests(TestCase):

    def setUp(self):
        b = ((-1.0, 1.0), (-1.0, 1.0), (-1.0, 1.0))
        points = [((sin(0.1*t), sin(0.2*t), sin(0.3*t)), t)
                  for t in range(50)]
        self.o1 = Octree(b)
        self.o1.extend(points)
        self.o2 = octree_from_list(b, points)

    def test_equality(self):
        self.assertEqual(self.o1, self.o2)


class GeometricTests(TestCase):

    def setUp(self):
        self.coords = set((sin(0.1*t), sin(0.2*t), sin(0.3*t))
                          for t in range(50))
        self.o = Octree(((-1.0, 1.0), (-1.0, 1.0), (-1.0, 1.0)))
        self.o.extend((p, True) for p in self.coords)

    def test_basic(self):
        self.assertEqual(len(self.o), 50)

    def test_get(self):
        for (i, p) in enumerate(self.coords):
            self.assertTrue(self.o.get(p, False))
        self.assertFalse(self.o.get((2.3, 3.4, 4.5), False))

    def test_by_distance_from_point(self):
        p = (0.123, 0.456, 0.789)

        l1 = list(self.o.by_distance_from_point(p))
        l2 = list(self.o.by_distance_from_point_rev(p))

        self.assertEqual(set(c for (_, c, _) in l1), self.coords,
                         """the points in order of distance from p should
                         be the same as the points we put in""")

        for (d, c, v) in l1:
            self.assertEqual(d, euclidean_point_point(p, c), """the
            points in order of distance from p should have distance
            computed correctly""")

        self.assertEqual(l1, list(reversed(l2)), """the points in
        order of distance reversed should be the reverse of the points
        in order of distance""")

        for ((d1, _, _), (d2, _, _)) in zip(l1, l1[1:]):
            self.assertTrue(d1 <= d2, """the points in order of
            distance from p should have increasing distance from p""")

        self.assertEqual(self.o.nearest_to_point(p), l1[0], """the
        nearest point to p should be the first in order of distance
        from p""")

        l3 = list(self.o.by_distance_from_point(p, 1.3))
        self.assertEqual(l3, l1[:len(l3)], """the points near p should
        be an initial segment of the points in order of distance from p""")

    def test_embiggen(self):
        b = ((-1.0, 1.6), (-1.0, 1.6), (-1.0, 1.6))
        o2 = self.o.rebound(b)
        self.assertEqual(o2.bounds, b)

        p = (0.653, -0.234, 0.113)
        l1 = list(self.o.by_distance_from_point(p))
        l2 = list(o2.by_distance_from_point(p))
        self.assertEqual(l1, l2, """enlarging the bounds shouldn't
        have changed the points""")

    def test_restrict(self):
        b = ((-1.57, 0.43), (-0.76, 0.83), (-0.37, 1.96))
        o2 = self.o.rebound(b)
        self.assertEqual(o2.bounds, b)

        p = (0.653, -0.234, 0.113)
        l1 = [(d, c, v)
              for (d, c, v) in self.o.by_distance_from_point(p)
              if point_in_box(c, b)]
        l2 = list(o2.by_distance_from_point(p))
        self.assertEqual(l1, l2, """playing around with the bounds
        should restrict the points""")

    def test_remove_all(self):
        p = (-0.432, 0.651, 0.791)
        l = list(self.o.by_distance_from_point(p))
        n = len(l)
        for (i, (_, c, _)) in enumerate(l):
            self.o.remove(c)
            self.assertEqual(len(self.o), n-i-1)
            with self.assertRaises(KeyError):
                self.o.remove(c)

    def test_union(self):
        p = (0.236, -0.532, -0.117)
        l = [c for (_, c, _) in self.o.by_distance_from_point(p)]

        o1 = Octree(((-1.0, 1.0), (-1.0, 1.0), (-1.0, 1.0)))
        o1.extend((p, True) for p in l[:25])
        self.assertEqual(len(o1), 25)

        o2 = Octree(((-1.0, 1.0), (-1.0, 1.0), (-1.0, 1.0)))
        o2.extend((p, True) for p in l[25:])
        self.assertEqual(len(o2), 25)

        self.assertEqual(o1.simple_union(o2), self.o)

    def test_matrix(self):
        m = ((0.123, 0.143, -0.987),
             (-0.345, 0.687, -0.431),
             (0.361, -0.183, 0.781))

        o1 = self.o.apply_matrix(m)

        s = set(matrix_action(m, p) for p in self.coords)
        self.assertEqual(len(s), len(self.coords))

        g1 = o1.by_distance_from_point((0.123, 0.456, 0.789))
        s1 = set(c for (_, c, _) in g1)
        self.assertEqual(s, s1)

    def test_iter_and_subset(self):
        l1 = set(t for (t, _) in self.o if sum(t) > 0)
        l2 = set(t for t in self.coords if sum(t) > 0)
        l3 = set(t for (t, _) in self.o.subset(lambda t: sum(t) > 0))

        self.assertEqual(l1, l2)
        self.assertEqual(l1, l3)

    def test_point_within_distance(self):
        epsilon = 0.1
        for t in range(150, 200):
            p = (sin(0.1*t), sin(0.2*t), sin(0.3*t))

            try:
                next(self.o.by_distance_from_point(p, epsilon))
                f_computed = True
            except StopIteration:
                f_computed = False

            f_real = False
            for (q, _) in self.o:
                if euclidean_point_point(p, q) < epsilon:
                    f_real = True
                    break

            self.assertEqual(f_computed, f_real)


class BinaryTests(TestCase):

    def setUp(self):
        self.coords1 = set((sin(0.1*t), sin(0.2*t), sin(0.3*t))
                           for t in range(50))
        self.o1 = Octree(((-1.0, 1.0), (-1.0, 1.0), (-1.0, 1.0)))
        self.o1.extend((p, None) for p in self.coords1)

        self.coords2 = set((sin(0.1*t), sin(0.2*t), sin(0.3*t))
                           for t in range(150, 200))
        self.o2 = Octree(((-1.0, 1.0), (-1.0, 1.0), (-1.0, 1.0)))
        self.o2.extend((p, None) for p in self.coords2)

    def test_proximity(self):
        l1 = []
        for c1 in self.coords1:
            (d, c2, _) = self.o2.nearest_to_point(c1)
            l1.append((d, c1, c2, None, None))
        l1.sort()
        l2 = list(self.o1.by_proximity(self.o2))
        self.assertEqual(l1, l2)

        l1b = list(t for t in l1 if t[0] < 0.1)
        l2b = list(self.o1.by_proximity(self.o2, 0.1))
        self.assertEqual(l1b, l2b)

    def test_isolation(self):
        l1 = []
        for c1 in self.coords1:
            (d, c2, _) = self.o2.nearest_to_point(c1)
            l1.append((d, c1, c2, None, None))
        l1.sort(reverse=True)
        l2 = list(self.o1.by_isolation(self.o2))
        self.assertEqual(l1, l2)

        l1b = list(t for t in l1 if t[0] > 0.3)
        l2b = list(self.o1.by_isolation(self.o2, 0.3))
        self.assertEqual(l1b, l2b)

    def test_pairs_by_distance(self):
        l1 = []
        for c1 in self.coords1:
            for c2 in self.coords2:
                d = euclidean_point_point(c1, c2)
                if d < 0.1:
                    l1.append((d, c1, c2, None, None))
        l1.sort()
        l2 = list(self.o1.pairs_by_distance(self.o2, 0.1))
        self.assertEqual(l1, l2)

    def test_pairs_nearby(self):
        s1 = set()
        for c1 in self.coords1:
            for c2 in self.coords2:
                d = euclidean_point_point(c1, c2)
                if d < 0.1:
                    s1.add((c1, c2, None, None))
        s2 = set(self.o1.pairs_nearby(self.o2, 0.1))
        self.assertEqual(s1, s2)
