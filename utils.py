def norm(s):
    """
    returns a normalized version of the given string, specifically
    lowercases and strips off punctuation within the string
    """
    return s.lower().replace("'", "")
