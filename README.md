# uvextras

Extra _custom_ features for `uv`

Inspired by the need for `pdm` _scripts_ feature set and an `uv info` command.

* [Features](#features)
* [Default Locations](#default-locations)
* [CLI](#cli)
* [Built-in Scripts](#built-in-scripts)

## Features

* _global_ scripts that `uv run` with `--no-project` or not - accessible from anywhere - e.g., `uvextras run clean`
* _global_ scripts installed to `$HOME/.local/share/uvextras/scripts`
* `uvextras` written in python; entrypoint installed to `$HOME/.local/share/uvextras/bin`
* _global_ (e.g., script) config can be overridden by local `.uvextras/uvextras.yaml` file
* _local_ scripts merged into list of available scripts by placing in `.uvextras/scripts/` dir
* `info` command that displays `uvextras` metadata and `uv` metadata (command missing in `uv`)


## Default Locations

| Default | Comment |
|  --- | --- |
| `$HOME/.config/uvextras/uvextras.yaml` | Config _extras_ features; _global_ defaults |
| `$HOME/.local/share/uvextras` | dir structure containing extras |
| `.uvextras` | local dir containing overrides / additions; override parts of config in local `.uvextras/uvextras.yaml` file |


## CLI

```
usage: python3 -m uvextras [-h] [-f FILE] (info | init | run) ...

options:
  -h, --help           show this help message and exit
  -f, --file FILE      path to the config file (default:
                       /var/home/klmcw/.config/uvextras/uvextras.yaml)

verbs:
  (info | init | run)
    info               show info about `uvextras` sub-system and `uv`
    init               wraps `uv init` with global default options
    run                run script
```

### info

```
usage: python3 -m uvextras info [-h] [--all] [-d] [-i] [-l] [-s] [-v]

show info about `uvextras` sub-system and `uv`

options:
  -h, --help       show this help message and exit
  --all            show local and global scripts (default: False)
  -d, --details    show details (default: False)
  -i, --info       hide info table (default: False)
  -l, --locations  hide locations (default: False)
  -s, --scripts    hide scripts (default: False)
  -v, --verbose    enable verbose output (default: False)
```

### init

_`init` is a work in progress_

```
usage: python3 -m uvextras init [-h] [-v]

wraps `uv init` with global default options

options:
  -h, --help     show this help message and exit
  -v, --verbose  enable verbose output (default: False)
```

### run

```
usage: python3 -m uvextras run [-h] [-v] script [args ...]

run script

positional arguments:
  script         name of script to execute
  args

options:
  -h, --help     show this help message and exit
  -v, --verbose  enable verbose output (default: False)
```

## Built-in Scripts

These are defined in [`uvextras.yaml`](./uvextras.yaml) and installed to `$HOME/.local/share/uvextras`.

| Script | Comment |
| --- | --- |
| `allclean` | Performs `clean` and `envclean` - like `distclean` but avoid that commonly used name |
| *  `clean` | Clean build artifacts - can override configured `items_to_delete` list (`__pycache__`, `*.o`, etc.) |
| *  `envclean` | Clean environment - can override configured `items_to_delete` list (e.g., `node_modules/`, `.venv/`, etc.) |
| `create` | re-create venv optionally using `--system-site-packages`  - see `uvextras.yaml` |
| `enable-dev` | adds dev group pkgs; override `pkgs` in project config |
| `gitignore` | Generates local `.gitignore` file using `git ignore` alias; override `features` locally (e.g. python,react ) |
