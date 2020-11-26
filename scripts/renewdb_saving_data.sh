#!/bin/bash

export start_pwd=$PWD
while [[ $PWD == *"scripts"* ]]; do
    cd ..
done

source ./scripts/auxiliary/prepare_launch.sh

if $(password_check); then
    pg_dump -Fc -Z0 --data-only -U orgfeed_user orgfeed_db > ./orgfeed_db_data.pgdump

    dropdb -U orgfeed_user orgfeed_db
    createdb -U orgfeed_user orgfeed_db
    psql orgfeed_db -U orgfeed_user < ./sql/orgfeed_db.sql

    pg_restore -U orgfeed_user --data-only -d orgfeed_db ./sql/orgfeed_db_data.pgdump
    rm -f ./orgfeed_db_data.pgdump
fi

cd $start_pwd
