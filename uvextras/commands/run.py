
import logging
import os
import subprocess

from uvextras.config import AppConfigScript
from uvextras.context import AppContext


def exec_dependencies(ctx: AppContext, script: AppConfigScript) -> None:
    for name in script.options['depends-on']:
        dscript = ctx.config.find_script(name)
        if dscript is not None:
            exec_script(ctx, dscript)
        else:
            logging.error(f'Script {name} is not known.')


def exec_script(ctx: AppContext, script: AppConfigScript) -> None:
    extra_args = ' '.join(ctx.args.args) if ctx.args.args else ''
    cmd = f'{script.cmd} {script.path(ctx.config.envvars)} {script.options_str} {extra_args}'

    if ctx.verbose:
        print(cmd)

    # disable venv
    environ = os.environ.copy()
    del environ['VIRTUAL_ENV']

    subprocess.call(cmd, shell=True, env=environ, text=ctx.verbose)


def cmd(ctx: AppContext) -> None:
    logging.debug('starting...')

    script = ctx.config.find_script(ctx.script)
    if script is not None:
        if 'depends-on' in script.options:
            exec_dependencies(ctx, script)

        if script.cmd is not None:
            exec_script(ctx, script)
    else:
        logging.error(f'Script {ctx.args.script} is not known.')

    logging.debug('done.')
