"""Functions integrating with the `rich` package"""

import os
import re
from pathlib import Path

from rich.console import Group
from rich.text import Text

from uvextras.context import AppContext

type RichRenderable = Text | Group | str

STYLE_CHECKMARK = 'bold green1'
STYLE_ENV_VAR = 'blue3'
STYLE_HIGHLIGHT = 'bold on wheat1'
STYLE_KEYWORD = 'bold yellow'
STYLE_SCRIPT_NAME = 'dark_red'
STYLE_SCRIPT_LOCAL_NAME = 'bold magenta'
STYLE_UV_KEY = 'bold spring_green4'
STYLE_UV_SEC = 'bold gray50'


def checkmark_if(pred: bool) -> str:
    return ':heavy_check_mark:' if pred else ''


def replace_dir(text: str, dir: str, replacement: str) -> str:
    rc: str = text
    replacement = replacement + '/'

    if dir in text:
        # print(f'Found {dir=} in {text=} => {replacement=}')
        name_re = rf'({dir})/'
        rc = re.sub(pattern=name_re, repl=replacement, string=text)

    return rc


def highlight_envvar_name(name: str, set_in_env: bool, style_if_not_set: str = STYLE_KEYWORD, highlight_if_set: str | None = STYLE_KEYWORD) -> Text:
    name_word = f'${name}'

    rc = Text(name_word, style=style_if_not_set)

    if set_in_env and highlight_if_set:
        rc.highlight_words(name_word, style=highlight_if_set)

    return rc


def stylize_dirs_from_ev(ctx: AppContext, text: str, binds: list[str]) -> RichRenderable:
    # replace locations in text
    for bind in binds:
        ev = ctx.config.envvars.find_bind(bind)
        loc = ctx.config.envvars[ev.bind]
        if loc is not None and Path.is_dir(loc):
            text = replace_dir(text, loc, f'${ev.name}')

    # replace home in text
    text = replace_dir(text, os.environ['HOME'], '$HOME')

    # Apply default style
    rc = Text(text, style='not bold default')

    # highlight $envvar occurences
    rc.highlight_regex(r'\$\w+', style=STYLE_ENV_VAR)

    return rc
