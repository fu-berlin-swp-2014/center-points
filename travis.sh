#! /usr/bin/env bash

set -e

nosetests --with-coverage --cover-package=centerpoints
./build-docs.sh
