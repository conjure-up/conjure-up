#!/usr/bin/python3

from collections import defaultdict
from functools import lru_cache
from subprocess import PIPE, run

from bundleplacer.charmstore_api import CharmStoreID
from bundleplacer.tarjan import strongly_connected_components


def graph_for_bundle(bundle, mc):
    s, _ = _graph_string_for_bundle(bundle, mc)
    out = run_graph_easy(s)
    return out


def scc_graph_for_bundle(bundle, mc):
    s, graph = _graph_string_for_bundle(bundle, mc)
    scc = strongly_connected_components(dict(graph))
    scc_graph = defaultdict(set)

    c_map = {}
    for component_tuple in scc:
        for item in component_tuple:
            c_map[item] = ", ".join(component_tuple)
    for src, dests in graph.items():
        for dest in dests:
            scc_graph[c_map[src]].add(c_map[dest])
    s = ""
    for src, dests in scc_graph.items():
        for dest in dests:
            s += "[ {} ] - > [ {} ]\n".format(src, dest)
    out = run_graph_easy(s)
    return out


@lru_cache(maxsize=2)
def run_graph_easy(graph_string):
    p = run("graph-easy --as boxart", input=graph_string, shell=True,
            stdout=PIPE, stderr=PIPE, universal_newlines=True)

    return p.stdout


def _graph_string_for_bundle(bundle, mc):
    s = []
    graph = defaultdict(list)
    svc_requires = {}
    svc_provides = {}
    for svc, sd in bundle._bundle['services'].items():

        csid = CharmStoreID(sd['charm'])
        info = mc.get_charm_info(csid.as_str_without_rev())
        if info is None:
            md = {}
        else:
            md = info['Meta']['charm-metadata']
        svc_requires[svc] = md.get("Requires", {})
        svc_provides[svc] = md.get("Provides", {})

    services_seen = set()
    for rel_src, rel_dst in bundle._bundle['relations']:
        def do_split(rel):
            ss = rel.split(":")
            if len(ss) == 1:
                return rel, ""
            else:
                return ss[0], ss[1]

        src, s_relname = do_split(rel_src)
        dst, d_relname = do_split(rel_dst)
        services_seen.add(src)
        services_seen.add(dst)

        if src not in svc_provides or src not in svc_requires or \
           dst not in svc_provides or dst not in svc_requires:
            continue
        src_provides = set([v['Interface'] for v in
                            svc_provides[src].values()])
        src_requires = set([v['Interface'] for v in
                            svc_requires[src].values()])
        dst_provides = set([v['Interface'] for v in
                            svc_provides[dst].values()])
        dst_requires = set([v['Interface'] for v in
                            svc_requires[dst].values()])

        provides_intersection = src_provides.intersection(dst_requires)
        is_provides = len(provides_intersection) == 1

        requires_intersection = src_requires.intersection(dst_provides)
        is_requires = len(requires_intersection) == 1

        srcunits = bundle._bundle['services'][src].get('num_units', 1)
        src_with_units = "{} \N{MULTIPLICATION SIGN} {}".format(src, srcunits)
        dstunits = bundle._bundle['services'][dst].get('num_units', 1)
        dst_with_units = "{} \N{MULTIPLICATION SIGN} {}".format(dst, dstunits)

        if is_provides:
            if s_relname == "":
                s_relname = [k for k, v in svc_provides[src].items() if
                             v['Interface'] ==
                             list(provides_intersection)[0]][0]
            if d_relname == "":
                d_relname = [k for k, v in svc_requires[dst].items() if
                             v['Interface'] ==
                             list(provides_intersection)[0]][0]

            if s_relname != d_relname:
                relname = s_relname + " \N{RIGHTWARDS ARROW} " + d_relname
            else:
                relname = s_relname
            line = "[{}] - {} -> [{}]".format(src_with_units, relname,
                                              dst_with_units)
            graph[src_with_units].append(dst_with_units)

        elif is_requires:
            if s_relname == "":
                s_relname = [k for k, v in svc_requires[src].items() if
                             v['Interface'] ==
                             list(requires_intersection)[0]][0]
            if d_relname == "":
                d_relname = [k for k, v in svc_provides[dst].items() if
                             v['Interface'] ==
                             list(requires_intersection)[0]][0]

            if s_relname != d_relname:
                relname = d_relname + " \N{RIGHTWARDS ARROW} " + s_relname
            else:
                relname = s_relname

            line = "[{}] - {} -> [{}]".format(dst_with_units, relname,
                                              src_with_units)
            graph[dst_with_units].append(src_with_units)
        else:
            line = ("[{}] <- {} \N{LEFT RIGHT ARROW} {} -> "
                    "[{}]").format(dst_with_units, s_relname,
                                   d_relname, src_with_units)
            graph[dst_with_units].append(src_with_units)
            graph[src_with_units].append(dst_with_units)
        s.append(line)

    for svc in bundle._bundle['services'].keys():
        if svc not in services_seen:
            s.append("[{}]".format(svc))
    return "\n".join(s), graph
