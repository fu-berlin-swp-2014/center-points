#! /usr/bin/env bash

set -e

nosetests
./build-docs.sh
