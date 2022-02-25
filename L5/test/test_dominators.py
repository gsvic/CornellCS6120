import os
import json

from L5.Dominators import find_dominators
from L5.Dominators import get_dominators_tree
from L5.Dominators import get_dominaton_frontiers
from pathlib import Path


def test_dominators():
    wd = Path(__file__).resolve().parent

    json_files = list(filter(lambda x: x.endswith(".json"), os.listdir(os.path.join(wd, "resources", "dominators"))))

    for jf in json_files:
        doms = find_dominators(open(os.path.join(wd, "resources", "dominators", jf)).read())
        out = json.loads(open(os.path.join(wd, "resources", "dominators", jf.split(".json")[0] + ".out")).read())

        for dom in doms:
            assert set(doms[dom]) == set(out[dom])

def test_domtree():
    wd = Path(__file__).resolve().parent

    json_files = list(filter(lambda x: x.endswith(".json"), os.listdir(os.path.join(wd, "resources", "domtree"))))

    for jf in json_files:
        doms = get_dominators_tree(open(os.path.join(wd, "resources", "domtree", jf)).read())
        out = json.loads(open(os.path.join(wd, "resources", "domtree", jf.split(".json")[0] + ".out")).read())

        for dom in doms:
            assert set(doms[dom]) == set(out[dom])

def test_frontiers():
    wd = Path(__file__).resolve().parent

    json_files = list(filter(lambda x: x.endswith(".json"), os.listdir(os.path.join(wd, "resources", "frontiers"))))

    for jf in json_files:
        doms = get_dominaton_frontiers(open(os.path.join(wd, "resources", "frontiers", jf)).read())
        out = json.loads(open(os.path.join(wd, "resources", "frontiers", jf.split(".json")[0] + ".out")).read())

        for dom in doms:
            assert set(doms[dom]) == set(out[dom])