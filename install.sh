#!/bin/bash

rm -fr ${HOME}/.local/share/uvextras
rm -fr ${HOME}/.config/uvextras

if [ "$1" != "-u" ]
then
    ./bin/uvextras run allclean

    mkdir -p ${HOME}/.local/share/uvextras/bin/
    cp -p bin/uvextras ${HOME}/.local/share/uvextras/bin/

    mkdir -p ${HOME}/.local/share/uvextras/
    cp -pr scripts/ ${HOME}/.local/share/uvextras/
    cp -pr uvextras/ ${HOME}/.local/share/uvextras/
    cp .python-version pyproject.toml uv.lock ${HOME}/.local/share/uvextras/

    mkdir -p ${HOME}/.config/uvextras/
    cp uvextras.yaml ${HOME}/.config/uvextras/

    cd ${HOME}/.local/share/uvextras/
    uvextras run create
fi
