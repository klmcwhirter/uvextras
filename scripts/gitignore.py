# /// script
# requires-python = ">=3.14"
# dependencies = []
# ///

import argparse
import os
import subprocess
import sys

parser = argparse.ArgumentParser()
parser.add_argument('-a', '--add-ons', default=None, type=str, action='store')
parser.add_argument('-f', '--features', default='python', action='store')
args = parser.parse_args(sys.argv[1:])

if os.path.exists('.gitignore'):
    os.unlink('.gitignore')

cmd = f'git ignore {args.features}'
subprocess.call(f'{cmd}', shell=True, text=True)

with open(".gitignore", "a") as gi:
    gi.write('\n')

    if args.add_ons is not None:
        print(f'{args.add_ons=}')
        add_on_lines = [f'{ao}\n' for ao in args.add_ons.split(',')]
        gi.writelines(add_on_lines)
