def has_valid_dimension(l, d=None):
    """Check congruent dimensions in a two-dimensional list."""
    if not l:
        return False

    if d is None:
        d = len(list[0])

    for sub in l:
        if len(sub) != d:
            return False

    return True


def has_valid_type(l, t):
    """ Check if every element in a two-dimensional list has the same type."""
    for sub in l:
        for e in sub:
            if type(e) != t:
                return False

    return True