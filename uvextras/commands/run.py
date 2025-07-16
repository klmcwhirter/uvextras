
import logging
import subprocess

from rich.pretty import pprint

from uvextras.config import AppConfigScript
from uvextras.context import AppContext


def exec_dependencies(ctx: AppContext, script: AppConfigScript) -> None:
    for s in script.options['depends-on']:
        exec_script(ctx, s)


def exec_script(ctx: AppContext, script: AppConfigScript) -> None:
    options = [
        f'--{o} "{v}"'
        for o, v in script.options.items()
    ]
    script_path = script.name if script.is_local else f'{ctx.config.envvars['scriptshome']}/{script.name}'
    cmd = f'{script.cmd} {script_path} {" ".join(options)}'

    if ctx.verbose:
        pprint(cmd)

    subprocess.call(cmd, shell=True, text=ctx.verbose)


def cmd(ctx: AppContext) -> None:
    logging.info(f'starting...')

    script = ctx.find_script(ctx.args.script)
    if 'depends-on' in script.options:
        exec_dependencies(ctx, script)

    if script.cmd is not None:
        exec_script(ctx, script)

    logging.info(f'done.')
