
import logging
import os
import subprocess
from typing import Mapping

from rich import box
from rich.console import Console
from rich.table import Table
from rich.text import Text

from uvextras.context import AppContext

STYLE_CHECKMARK = 'bold green1'
STYLE_HIGHLIGHT = 'bold on wheat1'
STYLE_KEYWORD = 'bold yellow'
STYLE_SCRIPT_LOC = 'blue3'
STYLE_SCRIPT_NAME = 'dark_red'
STYLE_SCRIPT_LOCAL_NAME = 'bold magenta'
STYLE_UV_KEY = 'bold spring_green4'

locations = [
    'config',
    'home',
    'scripts',
    'localdir',
    'localconfig',
    'localscripts',
]


def checkmark_if(pred: bool) -> str:
    return ':heavy_check_mark:' if pred else ''


HOME = os.environ['HOME']


def normalize_envvar(name: str) -> Text:
    rc = Text(f'${name}', style=STYLE_KEYWORD if name in os.environ else f'{STYLE_KEYWORD} not bold')
    return rc


def normalize_home(loc: str) -> Text | str:

    rc: Text | str = loc

    if loc.startswith(HOME):
        rc = normalize_envvar('HOME').append(loc.removeprefix(HOME), style='not bold default')

    return rc


def normalize_loc(ctx: AppContext, loc: str) -> Text | str:
    rc = normalize_path(ctx=ctx, path=loc, locations=['localdir', 'home'])

    if isinstance(rc, str):
        rc = normalize_home(rc)

    return rc


def normalize_path(ctx: AppContext, path: str, locations: list[str]) -> Text | str:
    rc: Text | str = path

    for loc in locations:
        loc_path = ctx.config.envvars[loc]
        if path.startswith(loc_path) and loc_path and path != loc_path:
            rc = path.removeprefix(loc_path)
            rc = Text(f'[{loc}]', style=STYLE_SCRIPT_LOC).append(rc, style='not bold default')
            break

    return rc


def shell_cli_output(cmd: str) -> str:
    return subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True, encoding='utf-8', text=True)


def uv_info(ctx: AppContext) -> Mapping[str, Text | str]:
    rc = {
        'UV Version': shell_cli_output('uv self version'),
        'Project Version': shell_cli_output('uv version'),
        'Cache Dir': normalize_home(shell_cli_output('uv cache dir')),
        'Tool Dir': normalize_home(shell_cli_output('uv tool dir')),
    }

    if ctx.details:
        rc |= {
            'Tool(s) Installed': shell_cli_output('uv tool list'),
            'Project Dependencies': shell_cli_output('uv tree --depth 1')
        }

    return rc


def print_locations(ctx: AppContext, console: Console) -> None:
    console.print()

    table = Table(title='Locations', title_justify='left', show_lines=True, box=box.ROUNDED)

    table.add_column('Type', style=STYLE_SCRIPT_LOC)

    if ctx.details:
        table.add_column('Override', STYLE_KEYWORD)

    table.add_column('Path')

    for ev in ctx.config.envvars.envvars:
        loc = ev.bind

        if ctx.details:
            table.add_row(loc, normalize_envvar(ev.name), normalize_loc(ctx, ctx.config.envvars[loc]))
        else:
            table.add_row(loc, normalize_loc(ctx, ctx.config.envvars[loc]))

    console.print(table)


def print_scripts(ctx: AppContext, console: Console) -> None:
    console.print()

    table = Table(title='Scripts', title_justify='left', show_lines=True, box=box.ROUNDED)

    table.add_column('Name', style=STYLE_SCRIPT_NAME)
    table.add_column('Depends')
    table.add_column('Desc')
    table.add_column('Local', justify='center', style=STYLE_CHECKMARK)

    if ctx.details:
        table.add_column('Cmd')

    table.add_column('Python ', justify='center', style=STYLE_CHECKMARK)

    if ctx.details:
        table.add_column('Path')
        table.add_column('Options')

    scripts = ctx.config.scripts
    if not ctx.all:
        scripts = [s for s in scripts if s.is_local]

    for s in sorted(scripts, key=lambda s: s.name):
        name = Text(s.name, style=STYLE_SCRIPT_LOCAL_NAME) if s.is_local else s.name
        depends = Text('\n'.join(s.depends_on), style=STYLE_HIGHLIGHT) if s.depends_on else ''

        if ctx.details:
            script_path = normalize_path(
                ctx=ctx,
                path=str(s.path(ctx.config.envvars)),
                locations=['scripts', 'localscripts']
            ) if s.use_python else ''
            options = '\n--'.join(s.options_str.split(' --'))
            table.add_row(name, depends, s.desc, checkmark_if(s.is_local), s.cmd, checkmark_if(s.use_python), script_path, options)
        else:
            table.add_row(name, depends, s.desc, checkmark_if(s.is_local), checkmark_if(s.use_python))

    console.print(table)


def print_uv_table(map: Mapping[str, Text | str], console: Console) -> None:
    console.print()

    table = Table(title='UV Info', title_justify='left', show_lines=True, box=box.ROUNDED)

    table.add_column('Item', style=STYLE_UV_KEY)
    table.add_column('Value')

    for k, v in map.items():
        table.add_row(k, v)

    console.print(table)


def cmd(ctx: AppContext) -> None:
    logging.debug('starting...')

    console = Console()

    if not ctx.uv:
        print_uv_table(uv_info(ctx), console)

    if not ctx.locations:
        print_locations(ctx, console)

    if not ctx.scripts:
        print_scripts(ctx, console)

    logging.debug('done.')
