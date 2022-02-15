import os
import subprocess
import json


class PyBril:
    def __init__(self, bril_binaries_path):
        """
        A minimal Python context for some Bril command-line tools
        :param bril_binaries_path: The Bril binaries path
        """
        self._bril_binaries_path = bril_binaries_path

    def bril2json(self, bril_input):
        """
        Executes the `bril2json` command-line command.
        :param bril_input: The .bril file
        :return: The JSON output
        """
        cmd = "{} < {}".format(os.path.join(self._bril_binaries_path, "bril2json"), bril_input)

        stdout, stderr = subprocess.Popen([cmd], shell=True, stdout=subprocess.PIPE,
                                          stderr=subprocess.STDOUT).communicate()

        return json.loads(stdout)
