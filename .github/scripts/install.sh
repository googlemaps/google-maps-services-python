#!/bin/bash

set -exo pipefail

if ! python3 -m pip --version; then
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    sudo python3 get-pip.py
    sudo python3 -m pip install --upgrade setuptools
    sudo python3 -m pip install nox twine
else
    sudo python3 -m pip install --upgrade setuptools
    python3 -m pip install nox
    python3 -m pip install --prefer-binary twine
fi
