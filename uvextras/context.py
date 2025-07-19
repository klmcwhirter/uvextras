
import argparse
import logging
from dataclasses import dataclass

from rich.logging import RichHandler
from rich.pretty import pprint

from uvextras.config import AppConfig


@dataclass
class AppContext:
    args: argparse.Namespace
    config: AppConfig

    def __post_init__(self) -> None:
        self._setup_logging()

    def __rich_repr__(self):
        yield 'args', self.args
        yield 'config', self.config

    @property
    def all(self) -> bool:
        return self.args.all if hasattr(self.args, 'all') else False

    @property
    def details(self) -> bool:
        return self.args.details if hasattr(self.args, 'details') else False

    @property
    def locations(self) -> bool:
        return self.args.locations if hasattr(self.args, 'locations') else False

    @property
    def script(self) -> str:
        return self.args.script

    @property
    def scripts(self) -> bool:
        return self.args.scripts if hasattr(self.args, 'scripts') else False

    @property
    def uv(self) -> bool:
        return self.args.uv if hasattr(self.args, 'uv') else False

    @property
    def verb(self) -> str:
        return self.args.verb

    @property
    def verbose(self) -> bool:
        return self.args.verbose

    def _setup_logging(self) -> None:
        log_level = logging.DEBUG if self.verbose else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='{asctime} - {module} - {funcName} - {message}', style='{',
            handlers=[RichHandler(omit_repeated_times=False, rich_tracebacks=True, tracebacks_show_locals=True)],
        )

    def log(self) -> None:
        if self.verbose:
            logging.debug(self.__class__.__name__)
            pprint(self)
