import os
from contextlib import contextmanager
from unittest.mock import MagicMock

from uvextras.config import AppConfigEnvVar, AppConfigEnvVarDict, resolve_envvar

@contextmanager
def temp_envvar(key: str, value: str):
    exists = key in os.environ
    old_val = os.environ[key] if exists else None

    try:
        os.environ[key] = value
        yield
    finally:
        if old_val is not None:
            os.environ[key] = old_val
        else:
            del os.environ[key]


def test_resolve_envvar_resolves_path() -> None:
    ev = AppConfigEnvVar(bind='config_module_file', name='OVERRIDE', resolve=['$PWD/uvextras/test_config.py'])
    bind, resolved = resolve_envvar(ev)

    assert bind == ev.bind
    assert resolved == __file__


def test_resolve_envvar_uses_envvar_value(monkeypatch) -> None:
    ev = AppConfigEnvVar(bind='config_module_file', name='OVERRIDE', resolve=['$PWD/uvextras/test_config.py'])

    monkeypatch.setenv(ev.name, 'bogus file path as override')
    bind, resolved = resolve_envvar(ev)
    env_var_val = os.environ[ev.name]

    print(f'\n{bind=}, {resolved=}, {env_var_val=}')

    assert bind == ev.bind
    assert resolved != __file__
    assert resolved == env_var_val


def test_resolve_envvar_returns_empty_if_no_path() -> None:
    ev = AppConfigEnvVar(bind='some_val', name='OVERRIDE', resolve=['not a valid path'])
    bind, resolved = resolve_envvar(ev)
    env_var_val = os.environ.get(ev.name, None)
    print(f'\n{bind=}, {resolved=}, {env_var_val=}')

    assert bind == ev.bind
    assert resolved != __file__
    assert resolved == ''


def test_AppConfigEnvVarDict_binds_resolved_val() -> None:
    ev = AppConfigEnvVar(bind='config_module_file', name='OVERRIDE', resolve=['$PWD/uvextras/test_config.py'])

    evd = AppConfigEnvVarDict([ev])

    assert evd[ev.bind] == __file__


def test_AppConfigEnvVarDict_uses_envvar(monkeypatch) -> None:
    ev = AppConfigEnvVar(bind='config_module_file', name='OVERRIDE', resolve=['$PWD/uvextras/test_config.py'])
    envvar_override = 'bogus file path as override'

    monkeypatch.setenv(ev.name, envvar_override)
    evd = AppConfigEnvVarDict([ev])

    bound_val = evd[ev.bind]

    assert evd is not None
    assert ev.bind in evd._bound
    assert bound_val == envvar_override


def test_AppConfigEnvVarDict_uses_bound(monkeypatch) -> None:
    ev = AppConfigEnvVar(bind='config_module_file', name='OVERRIDE', resolve=['$PWD/uvextras/test_config.py'])

    evd = AppConfigEnvVarDict([ev])
    assert ev.bind in evd._bound

    # verify that resolve_envvar was not called by mocking os.environ.keys() that is used by it
    mock_resolve = MagicMock()
    monkeypatch.setattr(os.environ, 'keys', mock_resolve)

    bound_val = evd[ev.bind]

    mock_resolve.assert_not_called()

    assert bound_val == __file__
