
import sys

from uvextras.cli import parse_args
from uvextras.commands import run

cmd_map = {
    'info': None,
    'init': None,
    'list': None,
    'run': run.cmd,
}


def main(args: list) -> None:
    ctx = parse_args(args=args)
    ctx.log()

    cmd = cmd_map[ctx.verb]
    cmd(ctx)


if __name__ == '__main__':
    main(sys.argv[1:])
