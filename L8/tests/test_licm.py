import json
import os

from pathlib import Path
from L8 import licm


def test_licm():
    wd = Path(__file__).resolve().parent
    loopcond_code = json.loads(open(os.path.join(wd, "resources", "loopcond.json")).read())

    refined = licm(loopcond_code)

    func_0_instrs = refined["functions"][0]["instrs"]

    # We expect a pre-header block here
    assert "prehead" in func_0_instrs[7]["label"]
    assert func_0_instrs[8]["dest"] == "inv"
    assert func_0_instrs[9]["dest"] == "uses_inv"