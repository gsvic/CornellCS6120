import os
import json

from L5.Dominators import find_dominators
from L5.Dominators import get_dominators_tree
from L5.Dominators import get_dominaton_frontiers
from pathlib import Path


def test_dominators():
    wd = Path(__file__).resolve().parent

    bril_files = list(filter(lambda x: x.endswith(".bril"), os.listdir(os.path.join(wd, "resources", "dominators"))))

    for bril in bril_files:
        doms = find_dominators(os.path.join(wd, "resources", "dominators", bril))
        out = json.loads(open(os.path.join(wd, "resources", "dominators", bril.split(".bril")[0] + ".out")).read())

        for dom in doms:
            assert set(doms[dom]) == set(out[dom])

def test_domtree():
    wd = Path(__file__).resolve().parent

    bril_files = list(filter(lambda x: x.endswith(".bril"), os.listdir(os.path.join(wd, "resources", "domtree"))))

    for bril in bril_files:
        doms = get_dominators_tree(os.path.join(wd, "resources", "domtree", bril))
        out = json.loads(open(os.path.join(wd, "resources", "domtree", bril.split(".bril")[0] + ".out")).read())

        for dom in doms:
            assert set(doms[dom]) == set(out[dom])

def test_frontiers():
    wd = Path(__file__).resolve().parent

    bril_files = list(filter(lambda x: x.endswith(".bril"), os.listdir(os.path.join(wd, "resources", "frontiers"))))

    for bril in bril_files:
        doms = get_dominaton_frontiers(os.path.join(wd, "resources", "frontiers", bril))
        out = json.loads(open(os.path.join(wd, "resources", "frontiers", bril.split(".bril")[0] + ".out")).read())

        for dom in doms:
            assert set(doms[dom]) == set(out[dom])