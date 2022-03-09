import json
import os

from pathlib import Path
from .is_ssa import is_ssa
from L6 import do_ssa


def test_loop():
    wd = Path(__file__).resolve().parent
    expected = json.loads(open(os.path.join(wd, "resources", "if-orig.json")).read())

    assert not is_ssa(expected)
    assert do_ssa(expected)