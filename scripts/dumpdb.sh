#!/bin/bash

export start_pwd=$PWD
while [[ $PWD == *"scripts"* ]]; do
    cd ..
done

source ./scripts/auxiliary/prepare_launch.sh

if $(password_check); then
    pg_dump -U orgfeed_user --schema-only orgfeed_db > ./sql/orgfeed_db.sql
    pg_dump -Fc -Z0 -U orgfeed_user --data-only orgfeed_db > ./sql/data.pgdump
fi

cd $start_pwd
