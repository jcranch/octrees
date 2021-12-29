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
Miscellaneous helper code

(C) James Cranch 2013--2021
"""

def pivot(l, f, start, stop):
    """
    Swap elements of l over so that, in the range l[start:stop], all
    elements satisfying f precede all those which don't.

    Returns the pivot point n such that l[start:n] all do and
    l[n:stop] all don't.
    """
    while start < stop:
        if f(l[start]):
            start += 1
        elif not f(l[stop-1]):
            stop -= 1
        else:
            (l[start], l[stop-1]) = (l[stop-1], l[start])
            start += 1
            stop -= 1
    return stop
