'''uvextras command line interface'''

import argparse

from uvextras.config import load_config
from uvextras.context import AppContext


def parse_args(args: list[str]) -> AppContext:
    config = load_config()

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-f', '--file', default=config.envvars['config'], help='path to the config file')

    verbs = parser.add_subparsers(title='verbs', required=True, dest='verb', metavar='(info | init | run)')

    info_desc = 'show info about `uvextras` sub-system and `uv`'
    info = verbs.add_parser(
        'info',
        description=info_desc,
        help=info_desc,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    info.add_argument('--all', default=False, action='store_true', help='show local and global scripts')
    info.add_argument('-d', '--details', default=False, action='store_true', help='show details')
    info.add_argument('-l', '--locations', default=False, action='store_true', help='hide locations')
    info.add_argument('-s', '--scripts', default=False, action='store_true', help='hide scripts')
    info.add_argument('-u', '--uv', default=False, action='store_true', help='hide uv info')
    info.add_argument('-v', '--verbose', default=False, action='store_true', help='enable verbose output')

    init_desc = 'wraps `uv init` with global default options'
    init = verbs.add_parser(
        'init',
        description=init_desc,
        help=init_desc,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    init.add_argument('-v', '--verbose', default=False, action='store_true', help='enable verbose output')

    run_desc = 'run script'
    run = verbs.add_parser(
        'run',
        description=run_desc,
        help=run_desc,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    run.add_argument('script', default=None, help='name of script to execute')
    run.add_argument('-v', '--verbose', default=False, action='store_true', help='enable verbose output')
    run.add_argument('args', nargs='*')

    pargs = parser.parse_args(args=args)
    ctx = AppContext(args=pargs, config=config)

    return ctx
