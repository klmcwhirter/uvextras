import sys
from typing import Mapping

from uvextras.cli import parse_args
from uvextras.commands import info, run
from uvextras.commands.type import CommandType

cmd_map: Mapping[str, CommandType] = {
    'info': info.cmd,
    'run': run.cmd,
}


def main() -> None:
    ctx = parse_args(args=sys.argv[1:])
    ctx.log()

    cmd = cmd_map[ctx.verb]
    cmd(ctx)


if __name__ == '__main__':
    main()
