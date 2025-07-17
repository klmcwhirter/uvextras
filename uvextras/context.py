
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
    def details(self) -> str:
        return self.args.details

    @property
    def local(self) -> str:
        return self.args.local

    @property
    def script(self) -> str:
        return self.args.script

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
