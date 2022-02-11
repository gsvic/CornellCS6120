import os
import subprocess

tdce_path = "../test/tdce"
tdce = os.listdir(tdce_path)

for f in tdce:
    cmd = "bril2json < {} | python3 dce.py | brili -p"
    path = os.path.join(tdce_path, f)
    print(cmd.format(path))
    subprocess.Popen("export PATH=$PATH:/Users/victorgiannakouris/.yarn/bin")
    out = subprocess.Popen("bril2json --help".format(path), shell=True, stdout=subprocess.PIPE).stdout.read()

    print(out)