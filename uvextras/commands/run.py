import logging
import os
import subprocess

from uvextras.config import AppConfigScript
from uvextras.context import AppContext


def exec_dependencies(ctx: AppContext, script: AppConfigScript) -> None:
    for name in script.depends_on:
        dscript = ctx.config.find_script(name)
        if dscript is not None:
            exec_script(ctx, dscript)
        else:
            logging.error(f'Script {name} is not known.')


def exec_script(ctx: AppContext, script: AppConfigScript) -> None:
    # this is needed to pass args through to cmd executed by script
    preamble = '-- ' if script.use_python else ''
    extra_args = preamble + ' '.join(ctx.args.args) if ctx.args.args else ''
    script_path = script.path(ctx.config.envvars) if script.use_python else ''
    cmd = f'{script.cmd} {script_path} {script.options_str} {extra_args}'

    if ctx.verbose:
        print(cmd)

    # disable venv
    environ = os.environ.copy()
    del environ['VIRTUAL_ENV']

    try:
        subprocess.call(cmd, shell=True, env=environ, text=ctx.verbose)
    except KeyboardInterrupt:
        pass


def cmd(ctx: AppContext) -> None:
    logging.debug('starting...')

    script = ctx.config.find_script(ctx.script)
    if script is not None:
        if script.depends_on:
            exec_dependencies(ctx, script)

        if script.cmd is not None:
            exec_script(ctx, script)
    else:
        logging.error(f'Script {ctx.args.script} is not known.')

    logging.debug('done.')
