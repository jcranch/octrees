# Some supporting 3D geometric code

from math import sqrt



def point_in_box(p,b):
    "Is p in b?"
    (x,y,z) = p
    ((minx,maxx), (miny, maxy), (minz, maxz)) = b
    return (minx <= x < maxx) and (miny <= y < maxy) and (minz <= z < maxz)


def box_contains(b1,b2):
    "Is all of b1 in b2?"
    ((minx1,maxx1), (miny1, maxy1), (minz1, maxz1)) = b1
    ((minx2,maxx2), (miny2, maxy2), (minz2, maxz2)) = b2
    return minx2 <= minx1 and maxx1 <= maxx2 and miny2 <= miny1 and maxy1 <= maxy2 and minz2 <= minz1 and maxz1 <= maxz2


def boxes_disjoint(b1,b2):
    "Are b1 and b2 disjoint?"
    ((minx1,maxx1), (miny1, maxy1), (minz1, maxz1)) = b1
    ((minx2,maxx2), (miny2, maxy2), (minz2, maxz2)) = b2
    return maxx2 <= minx1 or maxx1 <= minx1 or maxy2 <= miny1 or maxy1 <= miny1 or maxz2 <= minz1 or maxz1 <= minz1


def union_box(b1,b2):
    "The smallest box containing b1 and b2"
    ((minx1,maxx1), (miny1, maxy1), (minz1, maxz1)) = b1
    ((minx2,maxx2), (miny2, maxy2), (minz2, maxz2)) = b2
    return ((min(minx1,minx2),max(maxx1,maxx2)),(min(miny1,miny2),max(maxy1,maxy2)),(min(minz1,minz2),max(maxz1,maxz2)))


def vertices(bounds):
    "The vertices of a box"
    (xs,ys,zs) = bounds
    for x in xs:
        for y in ys:
            for z in zs:
                yield (x,y,z)


def subboxes(bounds):
    "The eight boxes contained within a box"
    ((minx, maxx), (miny, maxy), (minz, maxz)) = bounds
    midx = (maxx+minx)/2
    midy = (maxy+miny)/2
    midz = (maxz+minz)/2
    for bx in [(minx,midx),(midx,maxx)]:
        for by in [(miny,midy),(midy,maxy)]:
            for bz in [(minz,midz),(midz,maxz)]:
                yield (bx,by,bz)


def narrow(bounds, coords):
    "Narrow down a box to an appropriate subbox"

    ((minx, maxx), (miny, maxy), (minz, maxz)) = bounds

    midx = (maxx+minx)/2
    midy = (maxy+miny)/2
    midz = (maxz+minz)/2            

    (x,y,z) = coords

    if x < midx:
        r = 0
        newx = (minx,midx)
    else:
        r = 1
        newx = (midx,maxx)
    if y < midy:
        s = 0
        newy = (miny,midy)
    else:
        s = 1
        newy = (midy,maxy)
    if z < midz:
        t = 0
        newz = (minz,midz)
    else:
        t = 1
        newz = (midz,maxz)

    return ((r,s,t), (newx, newy, newz))


def euclidean_point_point(p,q):
    "The euclidean distance between points p and q"
    (x1,y1,z1) = p
    (x2,y2,z2) = q
    return sqrt((x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2)


def nearest_point_in_box(p,b):
    "Returns the nearest point in a box b to a point p"
    ((minx,maxx), (miny,maxy), (minz,maxz)) = b
    (x,y,z) = p
    if x<minx:
        x0 = minx
    elif x<maxx:
        x0 = x
    else:
        x0 = maxx
    if y<miny:
        y0 = miny
    elif y<maxy:
        y0 = y
    else:
        y0 = maxy
    if z<minz:
        z0 = minz
    elif z<maxz:
        z0 = z
    else:
        z0 = maxz
    return (x0,y0,z0)


def euclidean_point_box(p,b):
    "The euclidean distance between p and a box b"
    return euclidean_point_point(p,nearest_point_in_box(p,b))
