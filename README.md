# uvextras

Extra _custom_ features for `uv`

Inspired by the need for `pdm` _scripts_ feature set and an `uv info` command.

* [Features](#features)
* [Environment Variables](#environment-variables)
* [CLI](#cli)
* [Built-in Scripts](#built-in-scripts)

## Features

* _global_ scripts that `uv run` with `--no-project` or not - accessible from anywhere - e.g., `uvextras run clean`
* _global_ scripts installed to `$UVEXTRAS_HOME/scripts`
* `uvextras` written in python; entrypoint installed to `$UVEXTRAS_HOME/bin`
* _global_ config can be overridden by Environment Variables
* _global_ (e.g., script) config can be overridden by local `.uvextras/uvextras.yaml` file
* _local_ scripts merged into list of available scripts by placing in `.uvextras/scripts/` dir
* `info` command that displays `uvextras` metadata and `uv` metadata (command missing in `uv`)


## Environment Variables

| Env Var | Default | Comment |
| --- | --- | --- |
| `UVEXTRAS_CONFIG` | `~/.config/uvextras/uvextras.yaml` | Config _extras_ features; _global_ defaults |
| `UVEXTRAS_HOME` | `~/.local/share/uvextras` | dir structure containing extras |
| `UVEXTRAS_LOCAL_DIR` | `.uvextras` | local dir containing overrides / additions; override parts of config in local `.uvextras/uvextras.yaml` file |


## CLI

| Verb | Comment |
| --- | --- |
| `info` | show info about `uvextras` sub-system and `uv` |
| `init` | wraps `uv init` with global default options |
| `list` | show lists of objects (e.g., blended scripts list) |
| `run` | run script |


## Built-in Scripts

| Script | Comment |
| --- | --- |
| `allclean` | Performs `clean` and `envclean` - like `distclean` but avoid that commonly used name |
| *  `clean` | Clean build artifacts - can override configured `items_to_delete` list (`__pycache__`, `*.o`, etc.) |
| *  `envclean` | Clean environment - can override configured `items_to_delete` list (e.g., `node_modules/`, `.venv/`, etc.) |
| `create` | re-create venv optionally using `--system-site-packages`  - see `uvextras.yaml` |
| `gitignore` | Generates local `.gitignore` file using `git ignore` alias; override `features` locally (e.g. python,react ) |
