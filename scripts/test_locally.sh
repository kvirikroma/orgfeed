#!/bin/bash

export start_pwd=$PWD
while [[ $PWD == *"scripts"* ]]; do
    cd ..
done

source ./scripts/auxiliary/prepare_launch.sh

if $(password_check); then
    source ./.venv/bin/activate
    if command -v python3.9 > /dev/null; then
        python3.9 ./server.py
    elif command -v python3.8 > /dev/null; then
        python3.8 ./server.py
    elif command -v python3.7 > /dev/null; then
        python3.7 ./server.py
    else
        python3 ./server.py
    fi
fi

cd $start_pwd
