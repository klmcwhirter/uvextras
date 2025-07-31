# /// script
# requires-python = ">=3.14"
# dependencies = []
# ///

import argparse
import os
import subprocess
import sys

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--with-system', default=False, action='store_true')
args = parser.parse_args(sys.argv[1:])

# prevent warning that VIRTUAL_ENV is different
del os.environ['VIRTUAL_ENV']

subprocess.call('rm -fr .venv', shell=True, text=True)

cmd = f'uv venv{" --system-site-packages" if args.with_system else ""}'
subprocess.call(f'{cmd}', shell=True, text=True)

cmd = 'uv sync'
subprocess.call(f'{cmd}', shell=True, text=True)
