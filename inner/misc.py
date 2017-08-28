"""
Miscellaneous helper code
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
