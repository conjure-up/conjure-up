#!/usr/bin/env python

from collections import defaultdict
import argparse
import os
import re
from subprocess import PIPE, run

controllers_use_re = re.compile("(\s*)\S*\s*controllers\.use\('(.*)'\).render")
scope_re = re.compile("^(\s*)def (\w*)\(")

default_name_map = dict(spellpicker="Spell Selection",
                        bundlereadme="Spell Readme",
                        controllerselect="Controller Selection",
                        clouds="Cloud Selection",
                        bootstrapwait="Bootstrap Wait",
                        deploy="Charm List View & Charm Configuration",
                        deploystatus="Deploy Status",
                        steps="Actions List",
                        summary="Deploy Summary",
                        lxdsetup="LXD Configuration",
                        newcloud="New Cloud Credentials Setup",
                        START="Start")


def get_graph_string(filelist, opts):
    s = ""

    if opts.mapnames:
        name_map = default_name_map
    else:
        name_map = {}

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
                    label = ""
                    if not opts.nolabels:
                        label = "{}:{}".format(scopes[0], i+1)
                    s += "[ {} ] - {} -> [ {} ]\n".format(
                        name_map.get(src, src), label,
                        name_map.get(use_match.group(2),
                                     use_match.group(2)))
    if opts.condense:
        return "\n".join(set(s.splitlines()))
    return s


def get_files(kind):
    fl = []
    for root, dirs, files in os.walk('conjureup/controllers'):
        for name in files:
            if os.path.basename(name) == "{}.py".format(kind):
                fl.append(os.path.join(root, name))
    return fl


def run_graph_easy(graph_string, name, opts):
    p = run("graph-easy --output=controllers-{}.{}".format(name,
                                                           opts.fmt),
            input=graph_string, shell=True,
            stdout=PIPE, stderr=PIPE, universal_newlines=True)
    print(p.stderr)
    return p.stdout


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--nolabels", action="store_true")
    p.add_argument("--condense", action="store_true")
    p.add_argument("--mapnames", action="store_true")
    p.add_argument("--fmt", default='boxart')
    return p.parse_args()


if __name__ == "__main__":
    opts = parse_args()
    for t in ['gui', 'tui']:
        fl = get_files(t)
        s = get_graph_string(fl + [os.path.abspath('conjureup/app.py')], opts)
        print(t)
        print(run_graph_easy(s, t, opts))
