
def human_to_mb(s):
    """Translates human-readable strings like '10G' to numeric
    megabytes"""
    md = dict(M=1, G=1024, T=1024 * 1024, P=1024 * 1024 * 1024)
    return _human_to(s, md)


def human_to_gb(s):
    md = dict(M=1 / 1024, G=1, T=1024, P=1024 * 1024)
    return _human_to(s, md)


def _human_to(s, md):
    if len(s) == 0:
        raise Exception("unexpected empty string")

    suffix = s[-1].upper()
    if suffix.isalpha():
        return int(float(s[:-1]) * md[suffix])
    else:
        return int(s)


def mb_to_human(num):
    """Translates float number of bytes into human readable strings."""
    suffixes = ['M', 'G', 'T', 'P']
    return _to_human(num, suffixes)


def gb_to_human(num):
    """Translates float number of gigabytes into human readable strings."""
    suffixes = ['G', 'T', 'P']
    return _to_human(num, suffixes)


def _to_human(num, suffixes):
    if num == 0:
        return '0B'

    i = 0
    while num >= 1024 and i < len(suffixes) - 1:
        num /= 1024
        i += 1
    return "{:d}{}".format(num, suffixes[i])
