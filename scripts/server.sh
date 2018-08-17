#!/usr/bin/env bash

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

if [ -f ./scripts/vars.sh ]
then
    source ./scripts/vars.sh
else
    echo 'No variables found'
fi

case $1 in
    init)
        # init
        swap
        upgrade
        get_docker
        if [ -v swarm ] && ${swarm}
        then
            init_docker_swarm
        fi
        ;;
    deploy)
        deploy
        ;;
    run)
        secrets
        run $2
        ;;
    stop)
        stop
        ;;
    update)
        secrets
        # If vars exists then rea image list
        if [ -v img_list ]
        then
            for image in ${img_list[@]}
            do
              update_image ${image}
            done
        fi
        run
        ;;
    *)
        echo 'Unknown command'
        ;;
esac
