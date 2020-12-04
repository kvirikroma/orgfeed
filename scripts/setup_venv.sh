#!/bin/bash

export start_pwd=$PWD
while [[ $PWD == *"scripts"* ]]; do
    cd ..
done

if [ -d ./.venv ]; then
    export answer
    echo "Rewrite current venv?"
    read answer
    if [ $answer != "y" ]; then
        echo "Aborting"
        exit
    else
        if [[ "$VIRTUAL_ENV" != "" ]]; then
            echo "Deactivate current venv first!"
            exit
        fi
        rm -rf ./.venv
    fi
fi

export COMMAND
if command -v python3.9 > /dev/null; then
    COMMAND=python3.9
elif command -v python3.8 > /dev/null; then
    COMMAND=python3.8
elif command -v python3.7 > /dev/null; then
    COMMAND=python3.7
else
    COMMAND=python3
fi

if ! $COMMAND -m venv .venv; then
    if ! apt-get install -y python3-venv &&\
    python3 -m venv .venv; then
        echo "Error"
        exit
    fi
fi

source ./.venv/bin/activate &&\
pip3 install wheel &&\
#apt-get install -y postgresql-server-dev-all &&\
pip3 install -r ./requirements.txt &&\
deactivate

cd $start_pwd
