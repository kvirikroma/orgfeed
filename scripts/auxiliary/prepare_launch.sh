#!/bin/bash


while [[ $PWD == *"scripts"* ]]; do
    cd ..
done


function nopassword_check ()
{
    [[ $PGPASSWORD == '' ]]
    return $?
}

function password_check ()
{
    if $(nopassword_check); then
        return $(false)
    else
        return $(true)
    fi
}

function read_password ()
{
    if $(nopassword_check); then
        local password
        echo "Enter the PostgreSQL password:" > /dev/tty
        read -s password
    fi
    echo $password
}

function decrypt_key ()
{
    if
        local JWT_KEY=$(ccrypt -d ./scripts/encrypted_vars/jwt.cpt -c -K "$1" 2> /dev/null)
    then
        if [[ $JWT_KEY == '' ]]; then
            echo "Incorrect password" > /dev/tty
            echo ''
        fi
    else
        echo "Something went wrong" > /dev/tty
        echo ''
    fi
    echo $JWT_KEY
}

if [[ $PGPASSWORD == '' ]]; then
    export PGPASSWORD=$(read_password)
    export JWT_KEY=$(decrypt_key $PGPASSWORD)

    if [[ $JWT_KEY == '' ]]; then
        unset PGPASSWORD
    fi
fi
