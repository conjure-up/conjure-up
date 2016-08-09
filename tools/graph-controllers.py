#!python3

import os
import re
from subprocess import run, PIPE

controllers_use_re = re.compile("(\s*)\S*\s*controllers\.use\('(.*)'\).render")
scope_re = re.compile("^(\s*)def (\w*)\(")


def get_graph_string(filelist):
    s = "[ summary ] -> [ END ]\n"

    for fn in filelist:
        if os.path.basename(fn) == 'app.py':
            src = "START"
        else:
            src = os.path.dirname(fn).split('/')[-1]
        with open(fn, 'r') as f:
            scopes = [""]
            scope_indent = 0
            lines = f.readlines()

            for i in range(len(lines)):
                line = lines[i]
                scope_match = scope_re.search(line)
                if scope_match:
                    scope_indent = len(scope_match.group(1))
                    scopes.insert(0, scope_match.group(2))
                use_match = controllers_use_re.search(line)
                if use_match:
                    use_indent = len(use_match.group(1))
                    if use_indent <= scope_indent:
                        scopes.pop()
                    s += "[ {} ] - {} -> [ {} ]\n".format(
                        src, "{}:{}".format(scopes[0], i+1),
                        use_match.group(2))
    return s


def get_files(kind):
    fl = []
    for root, dirs, files in os.walk('conjureup/controllers'):
        for name in files:
            if os.path.basename(name) == "{}.py".format(kind):
                fl.append(os.path.join(root, name))
    return fl


def run_graph_easy(graph_string):
    p = run("graph-easy --as boxart", input=graph_string, shell=True,
            stdout=PIPE, stderr=PIPE, universal_newlines=True)
    print(p.stderr)
    return p.stdout


if __name__ == "__main__":
    for t in ['gui', 'tui']:
        fl = get_files(t)
        s = get_graph_string(fl + [os.path.abspath('conjureup/app.py')])
        print(t)
        print(run_graph_easy(s))
