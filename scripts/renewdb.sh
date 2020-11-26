#!/bin/bash

export start_pwd=$PWD
while [[ $PWD == *"scripts"* ]]; do
    cd ..
done

source ./scripts/auxiliary/prepare_launch.sh

if $(password_check); then
    dropdb -U orgfeed_user orgfeed_db
    createdb -U orgfeed_user orgfeed_db
    psql orgfeed_db -U orgfeed_user < ./sql/orgfeed_db.sql
    pg_restore -U orgfeed_user --data-only --disable-triggers -d orgfeed_db ./sql/data.pgdump
fi

cd $start_pwd
