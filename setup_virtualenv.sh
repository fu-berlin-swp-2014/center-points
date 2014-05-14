#! /usr/bin/env bash

if [ ! -d ".env" ];then
    pyvenv --copies .env
fi

source .env/bin/activate
pip install --upgrade -r requirements.txt
