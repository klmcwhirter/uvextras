#!/bin/bash

function simple_create
{
    if [ ! -d .venv ]
    then
        uv venv --system-site-packages
        uv sync "$@"
    fi
}

rm -fr ${HOME}/.local/share/uvextras
rm -fr ${HOME}/.config/uvextras

if [ "$1" != "-u" ]
then
    rm -fr .venv
    simple_create --no-dev
    uv run --no-project python -m uvextras run allclean

    mkdir -p ${HOME}/.local/share/uvextras/bin/
    cp -p bin/uvextras ${HOME}/.local/share/uvextras/bin/

    mkdir -p ${HOME}/.local/share/uvextras/
    cp -pr scripts/ ${HOME}/.local/share/uvextras/
    cp -pr uvextras/ ${HOME}/.local/share/uvextras/
    cp .python-version pyproject.toml uv.lock ${HOME}/.local/share/uvextras/

    mkdir -p ${HOME}/.config/uvextras/
    cp uvextras.yaml ${HOME}/.config/uvextras/

    simple_create

    cd ${HOME}/.local/share/uvextras/
    simple_create --no-dev
fi
