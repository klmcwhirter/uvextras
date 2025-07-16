
import logging
import subprocess

from rich.pretty import pprint

from uvextras.config import AppConfigScript
from uvextras.context import AppContext


def exec_dependencies(ctx: AppContext, script: AppConfigScript) -> None:
    for name in script.options['depends-on']:
        dscript = ctx.find_script(name)
        if dscript is not None:
            exec_script(ctx, dscript)
        else:
            logging.error(f'Script {name} is not known.')


def exec_script(ctx: AppContext, script: AppConfigScript) -> None:
    options = []
    for o, v in script.options.items():
        v = f' "{v}"' if v is not None else ""
        options.append(f'--{o}{v}')

    script_path = script.name if script.is_local else f'{ctx.config.envvars['scriptshome']}/{script.name}'
    script_path = f'{script_path}.py' if not script_path.endswith('.py') else script_path
    cmd = f'{script.cmd} {script_path} {" ".join(options)}'

    if ctx.verbose:
        pprint(cmd)

    subprocess.call(cmd, shell=True, text=ctx.verbose)


def cmd(ctx: AppContext) -> None:
    logging.info(f'starting...')

    script = ctx.find_script(ctx.script)
    if script is not None:
        if 'depends-on' in script.options:
            exec_dependencies(ctx, script)

        if script.cmd is not None:
            exec_script(ctx, script)
    else:
        logging.error(f'Script {ctx.args.script} is not known.')

    logging.info(f'done.')
