# /// script
# requires-python = ">=3.14"
# dependencies = []
# ///

import argparse
import os
import subprocess
import sys

parser = argparse.ArgumentParser()
parser.add_argument('--pkgs', default='autopep8 flake8', action='store')
args = parser.parse_args(sys.argv[1:])

# prevent warning that VIRTUAL_ENV is different
del os.environ['VIRTUAL_ENV']

subprocess.call(f'uv add --group dev {args.pkgs}', shell=True, text=True)
