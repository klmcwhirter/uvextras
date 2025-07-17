
import logging
from pathlib import Path

from rich import box
from rich.console import Console
from rich.table import Table
from rich.text import Text

from uvextras.context import AppContext

COLOR_SCRIPT_LOC = 'blue3'
COLOR_SCRIPT_NAME = 'dark_red'

locations = [
    'config',
    'home',
    'scripts',
    'localdir',
    'localconfig',
    'localscripts',
]


def cmd(ctx: AppContext) -> None:
    logging.debug('starting...')

    console = Console()

    if ctx.args.locations:
        print_locations(ctx, console)

    if ctx.args.scripts:
        print_scripts(ctx, console)

    logging.debug('done.')


def checkmark_if(pred: bool) -> str:
    return ':heavy_check_mark:' if pred else ''


def normalize_path(ctx: AppContext, path: Path) -> Text:
    text = Text()

    normalized_path = str(path)

    for loc in ['scripts', 'localscripts']:
        if normalized_path.startswith(ctx.config.envvars[loc]):
            text.append(f'[{loc}]', style=COLOR_SCRIPT_LOC)
            normalized_path = normalized_path.removeprefix(ctx.config.envvars[loc])
            break

    text.append(normalized_path)

    return text


def print_locations(ctx: AppContext, console: Console) -> None:
    console.print()

    table = Table(title='Locations', title_justify='left', show_lines=True, box=box.ROUNDED)

    table.add_column('Type', style=COLOR_SCRIPT_LOC)
    table.add_column('Path')

    for loc in locations:
        table.add_row(loc, ctx.config.envvars[loc])

    console.print(table)


def print_scripts(ctx: AppContext, console: Console) -> None:
    console.print()

    table = Table(title='Scripts', title_justify='left', show_lines=True, box=box.ROUNDED)

    table.add_column('Name', style=COLOR_SCRIPT_NAME)
    table.add_column('Depends')
    table.add_column('Desc')
    table.add_column('Local', justify='center', style='bold green1')

    if ctx.details:
        table.add_column('Cmd')

    table.add_column('Python ', justify='center', style='bold green1')

    if ctx.details:
        table.add_column('Path')
        table.add_column('Options')

    scripts = ctx.config.scripts
    if ctx.local:
        scripts = (s for s in scripts if s.is_local)

    for s in sorted(scripts, key=lambda s: s.name):
        name = Text(s.name, style='bold') if s.is_local else s.name
        depends = Text('\n'.join(s.depends_on), style='bold on wheat1') if s.depends_on else ''

        if ctx.details:
            script_path = normalize_path(ctx, s.path(ctx.config.envvars)) if s.use_python else ''
            options = '\n--'.join(s.options_str.split(' --'))
            table.add_row(name, depends, s.desc, checkmark_if(s.is_local), s.cmd, checkmark_if(s.use_python), script_path, options)
        else:
            table.add_row(name, depends, s.desc, checkmark_if(s.is_local), checkmark_if(s.use_python))

    console.print(table)
