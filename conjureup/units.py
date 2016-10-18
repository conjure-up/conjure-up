
def human_to_mb(s):
    """Translates human-readable strings like '10G' to numeric
    megabytes"""

    if len(s) == 0:
        raise Exception("unexpected empty string")

    md = dict(M=1, G=1024, T=1024 * 1024, P=1024 * 1024 * 1024)
    suffix = s[-1]
    if suffix.isalpha():
        return float(s[:-1]) * md[suffix]
    else:
        return float(s)


def mb_to_human(num):
    """Translates float number of bytes into human readable strings."""
    suffixes = ['M', 'G', 'T', 'P']
    if num == 0:
        return '0 B'

    i = 0
    while num >= 1024 and i < len(suffixes) - 1:
        num /= 1024
        i += 1
    return "{:.2f} {}".format(num, suffixes[i])
