'''The configuration concepts'''

from dataclasses import dataclass, field
import os
from pathlib import Path
from typing import Any


@dataclass
class AppConfigEnvVar:
    bind: str
    name: str
    resolve: list[str]


def resolve_envvar(ev: AppConfigEnvVar) -> tuple[str, str]:
    bind = ev.bind
    name = ev.name
    resolved = ''

    # env var overrides resolution process - short circuit
    if name in os.environ.keys():
        resolved = os.environ[name]
    elif ev.resolve is not None:
        # loop through the resolution rules and accept the first one that exists
        for r in ev.resolve:
            expanded = os.path.expandvars(r)
            path = Path(expanded).resolve()
            if path.exists(follow_symlinks=True):
                resolved = str(path)
                break
    return (bind, resolved)


@dataclass
class AppConfigEnvVarDict(dict[str, Any]):
    envvars: list[AppConfigEnvVar] = field(default_factory=list[AppConfigEnvVar], repr=False)

    def __post_init__(self):
        self._bound = {}

        for ev in self.envvars:
            _ = self[ev.bind]

    def __getitem__(self, key: str) -> Any:
        if key not in self._bound:
            evs = [e for e in filter(lambda ev: ev.bind == key, self.envvars)]
            if evs and len(evs) > 0:
                bind, resolved = resolve_envvar(evs[0])
                self._bound[bind] = resolved

        return self._bound[key]

    def __repr__(self) -> str:
        rc = f'{self.__class__.__name__}({self._bound})'
        return rc

    def __rich_repr__(self):
        for k, v in self._bound.items():
            yield k, v


@dataclass
class AppConfigScript:
    name: str
    desc: str
    cmd: str
    is_local: bool
    options: dict[str, Any]

    def __rich_repr__(self):
        yield 'name', self.name
        yield 'desc', self.desc
        yield 'cmd', self.cmd
        yield 'is_local', self.is_local
        yield 'options', self.options


@dataclass
class AppConfig:
    envvars: AppConfigEnvVarDict
    scripts: list[AppConfigScript]

    def __rich_repr__(self):
        yield 'envvars', self.envvars
        yield 'scripts', self.scripts

    @staticmethod
    def from_yaml(data: dict[str, Any]) -> AppConfig:
        envvars = AppConfigEnvVarDict(envvars=[
            AppConfigEnvVar(
                bind=ev.get('bind', ''),
                name=ev.get('name', ''),
                resolve=ev.get('resolve'),
            )
            for ev in data.get('envvars', [])
        ])

        scripts = [
            AppConfigScript(
                name=s.get('name'),
                cmd=s.get('cmd'),
                desc=s.get('desc', ''),
                is_local=s.get('is_local', True),
                options=s.get('options', {}),
            )
            for s in data.get('scripts', [])]
        return AppConfig(envvars, scripts)


BOOTSTRAP_CONFIG = {
    'config': '$HOME/.config/uvextras/uvextras.yaml',
    'home': '$HOME/.local/share/uvextras',
    'localdir': '.uvextras'
}


def load_config() -> AppConfig:
    config_file = os.path.expandvars(BOOTSTRAP_CONFIG['config'])
    file = config_file if os.path.exists(config_file) else 'uvextras.yaml'

    return load_config_for(file)


def load_config_for(file: str) -> AppConfig:
    from yaml import Loader, load
    with open(file, 'rb') as f:
        data = load(f, Loader=Loader)
    config = AppConfig.from_yaml(data)

    return config
