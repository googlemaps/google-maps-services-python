#!/bin/bash

rm -rf dist

python setup.py sdist
pip install $(find dist -name googlemaps-*.tar.gz)
