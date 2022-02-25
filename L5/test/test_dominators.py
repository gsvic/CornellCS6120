import os
import json

from pathlib import Path

from L5.Dominators import find_dominators
from L5.Dominators import get_dominators_tree
from L5.Dominators import get_dominaton_frontiers
from util import split_in_blocks
from util import add_terminators
from lib import CFG


def test_dominators():
    wd = Path(__file__).resolve().parent

    json_files = list(filter(lambda x: x.endswith(".json"), os.listdir(os.path.join(wd, "resources", "dominators"))))

    for jf in json_files:
        doms = find_dominators(open(os.path.join(wd, "resources", "dominators", jf)).read())
        out = json.loads(open(os.path.join(wd, "resources", "dominators", jf.split(".json")[0] + ".out")).read())

        for dom in doms:
            assert set(doms[dom]) == set(out[dom])

def test_check_dominators():
    wd = Path(__file__).resolve().parent

    json_files = list(filter(lambda x: x.endswith(".json"), os.listdir(os.path.join(wd, "resources", "dominators"))))

    for jf in json_files:
        doms = find_dominators(open(os.path.join(wd, "resources", "dominators", jf)).read())
        code = json.loads(open(os.path.join(wd, "resources", "dominators", jf)).read())

        for function in code["functions"]:
            blocks = split_in_blocks(function)
            blocks = add_terminators(blocks)

            cfg = CFG(blocks, add_entry_block=True)

            for block in doms:
                dominators = doms[block]
                for dominator in dominators:
                    assert cfg.check_dominator(root=list(cfg.get_nodes().keys())[0], block=block, dominated_by=dominator)


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