#! /usr/bin/env bash

CONDA_PACKETS='numpy|scipy|matplotlib|ipython'
CONDA_DEPS=$(grep -E $CONDA_PACKETS  requirements.txt | sed 's/==/=/')
PIP_DEPS=$(grep -vE $CONDA_PACKETS requirements.txt )
TRAVIS_PYTHON_VERSION=3.4

if [ ! -d "$HOME/miniconda3/envs/centerpoints/" ];then
    echo $CONDA_DEPS
    echo $PIP_DEPS
    conda create --yes -n centerpoints python=$TRAVIS_PYTHON_VERSION $CONDA_DEPS pip
fi

source activate centerpoints
pip install --upgrade  $PIP_DEPS
