import json
import numpy


def has_valid_dimension(l, d=None):
    """Check congruent dimensions in a two-dimensional list."""
    if not l:
        return False

    if d is None:
        d = len(l[0])

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


def chunks(l, n):
    """ Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


class NumpyAwareJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, numpy.ndarray) and obj.ndim == 1:
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)
