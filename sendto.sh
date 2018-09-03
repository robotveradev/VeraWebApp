#!/usr/bin/env bash

# if arguments provided
if [[ "$#" -lt 1 ]]
then
    echo 'no arguments'
fi

if ! [ -f vars.sh ]
then
    echo 'no variables file'
    exit 1
fi

source vars.sh

if [ -f functions.sh ]
then
    source ./functions.sh
elif [ -d scripts ] && [ -f ./scripts/functions.sh ]
then
    source ./scripts/functions.sh
else
    echo 'no functions found'
    exit 1
fi


package=package

# Create package directory
if ! [ -d ${package} ]
then
    mkdir ${package}
else
    # Clear package
    sudo rm -rf ${package}/*
fi


if check_host $1
then
    build vol_list[@] img_list[@] img_loc[@]
    mv volumes ${package}
    for f in ${send_list[@]}
    do
        if [ -e ${f} ]
        then
            cp -r ${f} ${package}
        fi
    done
    cd ${package}
    pack img_list
    send send_list[@] $1
    send_scripts $1 .
    if [ -v nginx ] && ${nginx}
    then
        send_nginx $1
    fi
else
    echo 'Host unreachable'
    exit 1
fi
