from collections import OrderedDict, defaultdict
from itertools import groupby


def norm(s):
    """
    returns a normalized version of the given string
    """
    return s.lower()


def normfind(iterable, text):
    """
    finds the first instance of text in iterable, which can be a dict or list
    normalizes before doing a comparison
    """
    text = norm(text)
    if isinstance(iterable, list):
        for v in iterable:
            if norm(v) == text:
                return v

    elif isinstance(iterable, dict):
        for k, v in iterable.items():
            if norm(k) == text:
                return v

    raise IndexError


def groupsortby(iterable, key=None):
    """
    Make an iterator that returns consecutive keys and groups from the
    iterable. The key is a function computing a key value for each element.
    If not specified or is None, key defaults to an identity function and
    returns the element unchanged.
    """
    for grp_name, grp_values in groupby(sorted(iterable, key=key),
                                        key=key):
        yield grp_name, list(grp_values)


def sorteddict(d, ordered_arr=None):
    """
    returns an OrderedDict from d in the order given by ordered_arr
    """
    #just return the dict with sorted keys
    if ordered_arr is None:
        return OrderedDict(sorted(d.items()))

    ret = OrderedDict()
    keys = list(d.keys())
    for k in ordered_arr:
        if k in keys:
            ret[k] = d[k]
    return ret


def group_items_by_level(items):
    grouped_items = defaultdict(list)
    for item in items:
        lvl = 0
        for req in item.requirements:
            if req.name == "Level":
                lvl = int(req.value)
                break
        grouped_items[lvl].append(item)
    return sorteddict(grouped_items)
