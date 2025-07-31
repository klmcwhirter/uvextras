# /// script
# requires-python = ">=3.14"
# dependencies = []
# ///

import argparse
import subprocess
import sys

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--items_to_delete', default='', required=True, metavar='items')
args = parser.parse_args(sys.argv[1:])

subprocess.call('find . -type d -name __pycache__ -exec rm -fr {} \\;', shell=True, text=True)

subprocess.call(f'rm -fr {args.items_to_delete}', shell=True, text=True)
