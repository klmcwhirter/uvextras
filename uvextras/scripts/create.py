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
parser.add_argument('-v', '--verbose', default=False, action='store_true')
args = parser.parse_args(sys.argv[1:])

# prevent warning that VIRTUAL_ENV is different
del os.environ['VIRTUAL_ENV']

cmd = 'rm -fr .venv'
if args.verbose:
    print(f'{cmd}')
subprocess.call(f'{cmd}', shell=True, text=True)

cmd = f'uv venv{" --system-site-packages" if args.with_system else ""}'
if args.verbose:
    print(f'{cmd}')
subprocess.call(f'{cmd}', shell=True, text=True)

cmd = 'uv sync --frozen'
if args.verbose:
    print(f'{cmd}')
subprocess.call(f'{cmd}', shell=True, text=True)
