"""The configuration concepts"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional, Self

from uvextras.shell import shell_cli_output


@dataclass
class AppConfigEnvVar:
    bind: str
    name: str
    resolve: list[str]
    set_in_env: bool = field(default=False, init=False)


def resolve_envvar(ev: AppConfigEnvVar) -> tuple[str, str]:
    bind = ev.bind
    name = ev.name
    resolved = ''

    # env var overrides resolution process - short circuit
    if name in os.environ:
        ev.set_in_env = True
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


UVEX_CONFIG = 'uvexconfig'
UVEX_HOME = 'uvexhome'
UVEX_SCRIPTS = 'uvexscripts'
UVEX_LOCALDIR = 'uvexlocaldir'
UVEX_LOCALCONFIG = 'uvexlocalconfig'
UVEX_LOCALSCRIPTS = 'uvexlocalscripts'
UV_PYTHON_INSTALL_DIR = 'uv_python_install_dir'
UV_TOOL_DIR = 'uv_tool_dir'

_env_var_keys = [
    UVEX_CONFIG,
    UVEX_HOME,
    UVEX_SCRIPTS,
    UVEX_LOCALDIR,
    UVEX_LOCALCONFIG,
    UVEX_LOCALSCRIPTS,
    UV_PYTHON_INSTALL_DIR,
    UV_TOOL_DIR,
]


@dataclass
class AppConfigEnvVarDict(dict[str, Any]):
    envvars: list[AppConfigEnvVar] = field(default_factory=list[AppConfigEnvVar], repr=False)

    def __post_init__(self):
        self._bound = {}

        # define $uvex_root so it can be used
        root = os.path.dirname(os.path.dirname(__file__))
        os.environ['uvex_root'] = root

        # Bind built-ins

        config = AppConfigEnvVarDict.config_ev()
        self.envvars.insert(0, config)

        for ev in AppConfigEnvVarDict.uv_envs():
            self.envvars.append(ev)

        for ev in self.envvars:
            _ = self[ev.bind]

    def __getitem__(self, key: str) -> Any:
        if key not in _env_var_keys:
            raise KeyError(f'{key} not allowed. Possibile values are one of {", ".join(_env_var_keys)}')

        if key not in self._bound:
            evs = [e for e in filter(lambda ev: ev.bind == key, self.envvars)]
            if evs and len(evs) > 0:
                ev = evs[0]
                bind, resolved = resolve_envvar(ev)
                self._bound[bind] = resolved

                # Enable ev.name to be used for future invocations of resolve_envvar(ev)
                os.environ[ev.name] = resolved

        return self._bound.get(key, None)

    def __setitem__(self, key: str, value: Any) -> None:
        if key not in _env_var_keys:
            raise KeyError(f'{key} not allowed. Possibile values are one of {", ".join(_env_var_keys)}')

        super().__setitem__(key, value)

    def __repr__(self) -> str:
        rc = f'{self.__class__.__name__}({self._bound})'
        return rc

    def __rich_repr__(self):
        for k, v in self._bound.items():
            yield k, v

    def find_bind(self, bind: str) -> AppConfigEnvVar:
        return [ev for ev in self.envvars if ev.bind == bind][0]

    @staticmethod
    def config_ev() -> AppConfigEnvVar:
        return AppConfigEnvVar(
            bind=UVEX_CONFIG,
            name='UVEX_CONFIG',
            resolve=[
                str(Path(os.path.dirname(__file__)) / 'uvextras.yaml'),
            ],
        )

    @staticmethod
    def uv_envs() -> list[AppConfigEnvVar]:
        return [
            AppConfigEnvVar(
                bind=UV_PYTHON_INSTALL_DIR,
                name='UV_PYTHON_INSTALL_DIR',
                resolve=[
                    shell_cli_output('uv python dir'),
                ],
            ),
            AppConfigEnvVar(
                bind=UV_TOOL_DIR,
                name='UV_TOOL_DIR',
                resolve=[
                    shell_cli_output('uv tool dir'),
                ],
            ),
        ]


@dataclass
class AppConfigScript:
    name: str
    desc: str
    depends_on: list[str]
    cmd: str
    use_python: bool
    is_local: bool
    env: dict[str, Any]
    options: dict[str, Any]

    def __rich_repr__(self):
        yield 'name', self.name
        yield 'desc', self.desc
        yield 'depends_on', self.depends_on
        yield 'cmd', self.cmd
        yield 'use_python', self.use_python
        yield 'is_local', self.is_local
        yield 'env', self.env
        yield 'options', self.options

    @property
    def options_str(self) -> str:
        options = []
        for o, v in self.options.items():
            v = f' "{v}"' if v is not None else ''
            options.append(f'--{o}{v}')
        return ' '.join(options)

    def merge(self, other: Self) -> None:
        for e in other.env:
            # override any specified env var settings
            self.env[e] = other.env[e]

        for o in other.options:
            # override any specified options
            self.options[o] = other.options[o]

        if other.depends_on:
            self.depends_on.extend(other.depends_on)

    def path(self, envvars: AppConfigEnvVarDict) -> Path:
        script_path = f'{envvars[UVEX_LOCALSCRIPTS]}/{self.name}' if self.is_local else f'{envvars[UVEX_SCRIPTS]}/{self.name}'
        script_path = f'{script_path}.py' if not script_path.endswith('.py') else script_path
        return Path(script_path)


@dataclass
class AppConfig:
    envvars: AppConfigEnvVarDict
    scripts: list[AppConfigScript]

    def __rich_repr__(self):
        yield 'envvars', self.envvars
        yield 'scripts', self.scripts

    @property
    def uv_py_dir(self) -> str:
        return self.envvars[UV_PYTHON_INSTALL_DIR]

    @property
    def uv_tool_dir(self) -> str:
        return self.envvars[UV_TOOL_DIR]

    def find_script(self, name: str) -> Optional[AppConfigScript]:
        rc = None

        filtered = [s for s in self.scripts if s.name == name]
        if len(filtered) > 0:
            rc = filtered[0]

        return rc

    def merge(self, other: Self) -> None:
        for s in other.scripts:
            if not s.is_local:
                # merge env, options and depends_on
                gs = self.find_script(s.name)
                if gs is not None:
                    gs.merge(s)
                else:
                    print(f'merge: script {s.name} not found')
            else:
                self.scripts.append(s)

    def merge_scripts(self, dir: Optional[str], desc: str) -> None:
        if not dir or dir is None:
            return

        def script_norm_name(p: Path) -> str:
            return str(p).removeprefix(str(path)).removeprefix('/').removesuffix('.py')

        path = Path(dir)
        if path.exists() and path.is_dir():
            filtered_script_names = [
                script_norm_name(p)
                for p in path.iterdir()
                if p.is_file() and str(p).endswith('.py') and not self.find_script(script_norm_name(p))
            ]

            self.scripts.extend(
                AppConfigScript(
                    name=name,
                    desc=desc,
                    depends_on=[],
                    cmd='',
                    use_python=True,
                    is_local=True,
                    env={},
                    options={},
                )
                for name in filtered_script_names
            )

    @staticmethod
    def from_yaml(data: dict[str, Any]) -> AppConfig:
        envvars = AppConfigEnvVarDict(
            envvars=[
                AppConfigEnvVar(
                    bind=ev.get('bind', ''),
                    name=ev.get('name', ''),
                    resolve=ev.get('resolve'),
                )
                for ev in data.get('envvars', [])
            ]
        )

        scripts = [
            AppConfigScript(
                name=s.get('name'),
                cmd=s.get('cmd'),
                depends_on=s.get('depends-on', []),
                use_python=s.get('use-python', True),
                desc=s.get('desc', ''),
                is_local=s.get('is-local', True),
                env=s.get('env', {}),
                options=s.get('options', {}),
            )
            for s in data.get('scripts', [])
        ]
        return AppConfig(envvars, scripts)


def load_config() -> AppConfig:
    config_ev = AppConfigEnvVarDict.config_ev()
    _, config_file = resolve_envvar(config_ev)
    config = load_config_for(config_file)

    local_config = config.envvars[UVEX_LOCALCONFIG]
    if os.path.exists(local_config):
        lcfg = load_config_for(local_config)
        config.merge(lcfg)

    config.merge_scripts(config.envvars[UVEX_LOCALSCRIPTS], desc='merged from local')

    return config


def load_config_for(file: str) -> AppConfig:
    from yaml import Loader, load

    with open(file, 'rb') as f:
        data = load(f, Loader=Loader)
    config = AppConfig.from_yaml(data)

    return config
