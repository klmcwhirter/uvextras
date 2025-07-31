# /// script
# requires-python = ">=3.14"
# dependencies = []
# ///

import argparse
import os
import subprocess
import sys

parser = argparse.ArgumentParser()
parser.add_argument('-a', '--addons', default=None, type=str, action='store')
parser.add_argument('-f', '--features', default='python', action='store')
args = parser.parse_args(sys.argv[1:])

if os.path.exists('.gitignore'):
    os.unlink('.gitignore')

cmd = f'git ignore {args.features}'
subprocess.call(f'{cmd}', shell=True, text=True)

with open(".gitignore", "a") as gi:
    gi.write('\n')

    if args.addons is not None:
        print(f'{args.addons=}')
        add_on_lines = [f'{ao}\n' for ao in args.addons.split(',')]
        gi.writelines(add_on_lines)
