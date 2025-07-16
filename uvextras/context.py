
import argparse
import logging
from dataclasses import dataclass

from rich.logging import RichHandler
from rich.pretty import pprint

from uvextras.config import AppConfig, AppConfigScript


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
    def verb(self) -> str:
        return self.args.verb

    @property
    def verbose(self) -> bool:
        return self.args.verbose

    def find_script(self, name: str) -> AppConfigScript:
        return [s for s in filter(lambda s: s.name == name, self.config.scripts)][0]

    def _setup_logging(self) -> None:
        log_level = logging.DEBUG if self.verbose else logging.INFO
        logging.basicConfig(
            level=log_level,
            # stream=sys.stdout,
            format='{asctime} - {module} - {funcName} - {message}', style='{',
            handlers=[RichHandler(omit_repeated_times=False, rich_tracebacks=True, tracebacks_show_locals=True)],
        )

    def log(self) -> None:
        if self.verbose:
            logging.debug(self.__class__.__name__)
            pprint(self)
