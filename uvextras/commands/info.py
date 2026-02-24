import logging
import os
import sys
from functools import partial
from typing import Mapping

from rich import box
from rich.console import Console, Group
from rich.table import Table
from rich.text import Text

from uvextras.config import (
    UV_PYTHON_INSTALL_DIR,
    UV_TOOL_DIR,
    UVEX_HOME,
    UVEX_LOCALDIR,
    UVEX_LOCALSCRIPTS,
    UVEX_SCRIPTS
)
from uvextras.context import AppContext
from uvextras.shell import shell_cli_output
from uvextras.stylize import (
    STYLE_CHECKMARK,
    STYLE_ENV_VAR,
    STYLE_HIGHLIGHT,
    STYLE_KEYWORD,
    STYLE_SCRIPT_LOCAL_NAME,
    STYLE_SCRIPT_NAME,
    STYLE_UV_KEY,
    STYLE_UV_SEC,
    RichRenderable,
    checkmark_if,
    highlight_envvar_name,
    stylize_dirs_from_ev
)

locations = [
    # These are in priority order -> more specific to less specific
    UVEX_LOCALSCRIPTS,
    UVEX_LOCALDIR,
    UVEX_SCRIPTS,
    UVEX_HOME,
    UV_TOOL_DIR,
    UV_PYTHON_INSTALL_DIR,
]

_stylize_dirs_with_ev = partial(stylize_dirs_from_ev, binds=locations)


def uv_info(ctx: AppContext) -> Mapping[str, Mapping[str, RichRenderable]]:
    project = {
        'Version': shell_cli_output('unset VIRTUAL_ENV;uv version'),
        'Python Version': shell_cli_output("unset VIRTUAL_ENV;uv run python -c 'import sys; print(sys.version.split()[0])'"),
        'Python Location': _stylize_dirs_with_ev(
            ctx,
            os.path.realpath(
                shell_cli_output("unset VIRTUAL_ENV;uv run python -c 'import sys; print(sys.executable)'"),
            ),
        ),
    }

    if ctx.details:
        project |= {
            'Dependencies': shell_cli_output('unset VIRTUAL_ENV;uv tree --all-groups --depth 1'),
        }

    uv = {
        'Version': shell_cli_output('uv self version'),
        'Cache Dir': _stylize_dirs_with_ev(ctx, shell_cli_output('uv cache dir')),
        'Python Install Dir': _stylize_dirs_with_ev(ctx, ctx.config.uv_py_dir),
        'Tool Dir': _stylize_dirs_with_ev(ctx, ctx.config.uv_tool_dir),
    }

    if ctx.details:
        py_vers = shell_cli_output('uv python list --only-installed --managed-python', redirect_stderr=True)
        uv_python_vers = [_stylize_dirs_with_ev(ctx, ln) for ln in py_vers.splitlines()]

        uv |= {
            'Python Version(s) Installed': Group(*uv_python_vers),
            'Tool(s) Installed': _stylize_dirs_with_ev(ctx, shell_cli_output('uv tool list --show-paths', redirect_stderr=True)),
        }

    uvextras = {
        'Version': '0.1.0',
        'Python Version': sys.version.split()[0],
        'Python Location': _stylize_dirs_with_ev(ctx, os.path.realpath(sys.executable)),
    }

    return {
        'uv': uv,
        'uvextras': uvextras,
        'Project': project,
    }


def print_locations(ctx: AppContext, console: Console) -> None:
    console.print()

    table = Table(title='Locations', title_justify='left', show_lines=True, box=box.ROUNDED)

    table.add_column('Item', style=STYLE_ENV_VAR)

    if ctx.details:
        table.add_column('Override', STYLE_KEYWORD)

    table.add_column('Path')

    for ev in ctx.config.envvars.envvars:
        loc = ev.bind

        if ctx.details:
            table.add_row(
                loc,
                highlight_envvar_name(
                    ev.name,
                    ev.set_in_env,
                    style_if_not_set=f'{STYLE_KEYWORD} not bold dim',
                    highlight_if_set=f'default {STYLE_KEYWORD} bold on wheat1',
                ),
                _stylize_dirs_with_ev(ctx, ctx.config.envvars[loc]),
            )
        else:
            table.add_row(loc, _stylize_dirs_with_ev(ctx, ctx.config.envvars[loc]))

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
            script_path = _stylize_dirs_with_ev(ctx=ctx, text=str(s.path(ctx.config.envvars))) if s.use_python else ''
            options = '\n--'.join(s.options_str.split(' --'))
            if s.env:
                options += '\n\nEnv Vars:'
                for e in  s.env:
                    options += f'\n${e}={s.env[e]}'
                options = _stylize_dirs_with_ev(ctx=ctx, text=options)
            table.add_row(name, depends, s.desc, checkmark_if(s.is_local), s.cmd, checkmark_if(s.use_python), script_path, options)
        else:
            table.add_row(name, depends, s.desc, checkmark_if(s.is_local), checkmark_if(s.use_python))

    console.print(table)


def print_uv_table(map: Mapping[str, Mapping[str, RichRenderable]], console: Console) -> None:
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
