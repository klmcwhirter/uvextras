import logging
import os
import re
import subprocess
from typing import Mapping

from rich import box
from rich.console import Console, Group
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
STYLE_UV_SEC = 'bold gray50'

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


def normalize_envvar_dir(text: str, name: str, dir: str) -> Text | str:
    rc: Text | str = text

    if dir in text:
        name_re = rf'({dir})'
        name_replace = f'${name}'
        replaced = re.sub(name_re, name_replace, text)

        rc = Text(replaced, style='not bold default')
        rc.highlight_words(name_replace, style=STYLE_KEYWORD)

    return rc


def normalize_envvar_name(name: str, style_if_not_set: str = STYLE_KEYWORD, highlight_if_set: str | None = STYLE_KEYWORD) -> Text:
    name_word = f'${name}'

    rc = Text(name_word, style=style_if_not_set)

    if name in os.environ and highlight_if_set:
        rc.highlight_words(name_word, style=highlight_if_set)

    return rc


def normalize_loc(ctx: AppContext, loc: str) -> Text | str:
    rc = normalize_path(ctx=ctx, path=loc, locations=['localdir', 'home'])

    if isinstance(rc, str):
        rc = normalize_user_home(rc)

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


def normalize_user_home(text: str) -> Text | str:
    return normalize_envvar_dir(text, 'HOME', os.environ['HOME'])


def normalize_uv_or_home(text: str, uv_py_dir: str) -> Text | str:
    rc = normalize_envvar_dir(text, 'UV_PYTHON_INSTALL_DIR', uv_py_dir)

    if isinstance(rc, str):
        # try home
        rc = normalize_user_home(rc)

    return rc


def shell_cli_output(cmd: str, redirect_stderr=False) -> str:
    stderr = subprocess.STDOUT if redirect_stderr else None
    return subprocess.check_output(cmd, stderr=stderr, shell=True, encoding='utf-8', text=True).strip()


def uv_info(ctx: AppContext) -> Mapping[str, Text | Group | str]:
    uv_py_dir = shell_cli_output('uv python dir')

    uvextras = {
        'Version': shell_cli_output(f'uv --project {ctx.config.envvars["home"]} version'),
        'Python Version': shell_cli_output(f'uv run --project {ctx.config.envvars["home"]} python --version'),
        'Python Location': normalize_uv_or_home(
            shell_cli_output(f'readlink `uv run --project {ctx.config.envvars["home"]} which python`'),
            uv_py_dir,
        ),
    }
    project = {
        'Version': shell_cli_output('uv version'),
        'Python Version': shell_cli_output('uv run --active python --version'),
        'Python Location': normalize_uv_or_home(
            shell_cli_output('readlink `uv run --active which python`'),
            uv_py_dir,
        ),
    }

    if ctx.details:
        project |= {
            'Dependencies': shell_cli_output('uv tree --all-groups --depth 1'),
        }

    uv = {
        'Version': shell_cli_output('uv self version'),
        'Cache Dir': normalize_user_home(shell_cli_output('uv cache dir')),
        'Python Install Dir': normalize_user_home(uv_py_dir),
        'Tool Dir': normalize_user_home(shell_cli_output('uv tool dir')),
    }

    if ctx.details:
        py_vers = shell_cli_output('uv python list --only-installed --managed-python', redirect_stderr=True)
        uv_python_vers = [normalize_uv_or_home(ln, uv_py_dir) for ln in py_vers.splitlines()]

        uv |= {
            'Python Version(s) Installed': Group(*uv_python_vers),
            'Tool(s) Installed': shell_cli_output('uv tool list', redirect_stderr=True),
        }

    return {
        'uv': uv,
        'uvextras': uvextras,
        'Project': project,
    }


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
            table.add_row(
                loc,
                normalize_envvar_name(
                    ev.name,
                    style_if_not_set=f'{STYLE_KEYWORD} not bold dim',
                    highlight_if_set=f'default {STYLE_KEYWORD} bold on wheat1',
                ),
                normalize_loc(ctx, ctx.config.envvars[loc]),
            )
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
            script_path = (
                normalize_path(
                    ctx=ctx,
                    path=str(s.path(ctx.config.envvars)),
                    locations=['scripts', 'localscripts'],
                )
                if s.use_python
                else ''
            )
            options = '\n--'.join(s.options_str.split(' --'))
            table.add_row(name, depends, s.desc, checkmark_if(s.is_local), s.cmd, checkmark_if(s.use_python), script_path, options)
        else:
            table.add_row(name, depends, s.desc, checkmark_if(s.is_local), checkmark_if(s.use_python))

    console.print(table)


def print_uv_table(map: Mapping[str, Text | str], console: Console) -> None:
    console.print()

    table = Table(title='Info', title_justify='left', show_lines=True, box=box.ROUNDED)

    table.add_column('Item', style=STYLE_UV_KEY)
    table.add_column('Value')

    for s, m in map.items():
        table.add_row(Text(s.upper(), style=STYLE_UV_SEC), end_section=True)

        for k, v in m.items():
            table.add_row('  ' + k, v)

    console.print(table)


def cmd(ctx: AppContext) -> None:
    logging.debug('starting...')

    console = Console()

    if not ctx.hide_uv:
        print_uv_table(uv_info(ctx), console)

    if not ctx.hide_locations:
        print_locations(ctx, console)

    if not ctx.hide_scripts:
        print_scripts(ctx, console)

    logging.debug('done.')
