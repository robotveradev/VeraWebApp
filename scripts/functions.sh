#!/usr/bin/env bash

# Compile directory structure
# usage: build volume_list[@] image_name[@] image_src[@]
build() {

    if [[ $# -lt 3 ]]
    then
        echo "wrong arguments"
        exit 1
    fi

    local vol_list=("${!1}")
    local image_name=("${!2}")
    local image_src=("${!3}")

    echo "Collecting volumes..."

    if ! [ -d volumes ]
    then
        mkdir volumes
    fi

    for f in ${vol_list[@]}
    do
        # create if not exists
        if [ -d ${f} ]
        then
            cp -r ${f} ./volumes
        elif ! [ -d ./volumes/$(basename ${f}) ]
        then
            mkdir ./volumes/$(basename ${f})
        fi
        #cp -r ${f} ./volumes
    done

    # Build images
    echo "Building images..."
# sudo docker build -t ${image_name} ${image_src}
# tag if needed :$(date +%Y%m%d%H%M%S)

    for img in ${image_name[@]}
    do
        sudo docker build -t ${img}:latest ${image_src[${img}]}
    done
}

# Pack project files
# usage: pack image_list
pack() {

    if [[ $# -lt 1 ]]
    then
        echo "wrong arguments"
        exit 1
    fi

    local img_list=("${!1}")

    echo "Collecting images..."

    if ! [ -e images ]
    then
        mkdir images
    fi

    for name in ${img_list[@]}
    do
        sudo docker save ${name} | gzip > ./images/${name}.tgz
    done

    echo "Compress volumes..."
    tar -czf volumes.tgz volumes/

    echo "Compress images..."
    tar -cf images.tgz images/
}

# Check remote availability
# usage: check_host root@127.0.0.1
check_host() {

    # Check if first argument exists and is valid remote host address
    if [ $# -eq 0 ]
    then
        echo "No arguments supplied"
        exit
    fi

    status=$(ssh -o BatchMode=yes -o ConnectTimeout=5 $1 echo ok 2>&1)

    if [[ ${status} != ok ]]
    then
        echo Connection ERROR: ${status}
        false
    else
        true
    fi
}

# Send files in list to remote host
# usage: send send_files_list remote_host
send() {

    if [[ $# -lt 1 ]]
    then
        echo "wrong arguments"
        exit 1
    fi

    # TODO check second argument and default_path exists or rise error

    local send_list=("${!1}")
    local REMOTE_HOST=$2

    # Try to create directory on remote host
    if [ -v default_path ] && [ -n ${default_path} ]
    then
        # ssh remote-host 'mkdir -p foo/bar/qux'
        # ssh ${REMOTE_HOST} 'mkdir -p /opt/${default_path}'
        rsync /dev/null ${REMOTE_HOST}:/opt/${default_path}/
    fi

    echo "Sending to server..."
    for file in ${send_list[@]}
    do
        scp ./${file} ${REMOTE_HOST}:/opt/${default_path}
    done
}

# Send service scripts to remote host
# usage: send_scripts remote_host
send_scripts() {
    local REMOTE_HOST=$1
    declare -a scripts=(
                        "./scripts/server.sh"
                        "./scripts"
                        )

    echo "Sending scripts..."
    for file in ${scripts[@]}
    do
        scp -r ${file} ${REMOTE_HOST}:/opt/${default_path}
    done
    # Send vars
    scp $2/vars.sh ${REMOTE_HOST}:/opt/${default_path}/scripts

}

# Send nginx directory to server
# usage: send_nginx remote_host
send_nginx() {
    local REMOTE_HOST=$1
    scp -r ./nginx ${REMOTE_HOST}:/opt/
}


## SERVER SIDE

# Update project image by name
# Force docker reread image with same name from disk
# usage: update_image image_name
update_image() {

    if [[ $# -ne 1 ]]
    then
        echo "wrong arguments"
        exit 1
    fi

    local image=$1

    local names=$(sudo docker service ls --format "{{.Name}}:{{.Image}}" | grep ${image})

    declare -a array=()
    for name in ${names}
    do
        array+=("${name%%:*}")
    done

    local unique_names=($(echo "${array[@]}" | tr ' ' '\n' | sort -u | tr '\n' ' '))

    for service in ${unique_names[@]}
    do
        echo "Updating..."
        sudo docker service update --force ${service}
        #Todo check is all images updated
    done
}

# Deploy files and images from archives
# usage: deploy
deploy() {
    echo "Extracting files..."

    tar -xf images.tgz
    tar -xf volumes.tgz

    if ! [ -d 'images' ]
    then
        echo "No image directory found"
        exit 1
    fi

    echo "Import images..."

    for f in ./images/*
    do
        docker load -i ${f}
    done
}

# Install secrets into docker swarm
# usage secrets
secrets () {
    # check if secrets directory exists
    if ! [ -d ./secrets ]
    then
        echo "No secrets found"
        return 0
    fi

    for file in ./secrets/*
    do
        local name=${file##*/}
        name=${name%.*}
        echo ${name}
        local status=($(sudo docker secret ls --filter "name=${name}" -q))
        if [ -z ${status[@]} ]
        then
            sudo docker secret create ${name} ${file}
        else
            echo "Secret [${name}] already exists"
        fi
    done
}

# Run docker stack
# Require stack name at first run, save it to stackname file
# usage: run [stack name]
run() {
    stack=$(get_stack_name)
    if [ -f stackname ]
    then
        if [ -z ${stack} ]
        then
            echo 'no stack name found'
            exit 1
        else
            sudo docker stack deploy -c docker-compose.yml ${stack}
        fi
    elif [ $# -ne 0 ]
    then
        sudo docker stack deploy -c docker-compose.yml $1
        echo $1 > stackname

    else
        echo 'no arguments provided'
    fi
}

# Stop current running stack if find stackname file
# usage: stop
stop() {
    if ! [ -f stackname ]
    then
        echo 'No stack name found'
    fi

    local stack=$(<stackname)

    docker stack rm ${stack}
}

# Trying to get stack name saved in file stackname
# usage: get_stack_name
get_stack_name() {
    # if stackname file exists
    if [ -f stackname ]
    then
        local value=$(<stackname)
        echo ${value}
    fi
}


## Initialize
# usage: swap
# Create and enable swap file if not exists
# default size 4Gb
swap() {
    if [[ $(swapon --show=SIZE --noheadings) ]]
    then
        echo "Swap already exists"
        return 0
    fi
    # setup swap
    fallocate -l 4G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo "/swapfile   none    swap    sw    0   0" >> /etc/fstab
}

# upgrade os
# usage: upgrade
upgrade() {
    sudo apt update
    sudo apt -y upgrade
}

# Install docker-ce on system
# usage: get_docker
get_docker() {

    if [[ $(which docker) ]]
    then
        echo "Docker already installed"
        # Todo update
        exit 0
    fi

    echo "Install Docker"
    sudo apt update
    # Install packages to allow apt to use a repository over HTTPS
    sudo apt -y install \
                apt-transport-https \
                ca-certificates \
                curl \
                software-properties-common
    # Add Docker’s official GPG key
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
    sudo add-apt-repository \
        "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
        $(lsb_release -cs) \
        stable"

    sudo apt update
    # docker-ce not yet ready for ubuntu 18
    # use docker.io so
    if [[ $(sudo apt -qq list docker-ce) ]]
    then
        sudo apt -y install docker-ce
    elif [[ $(sudo apt -qq list docker.io) ]]
    then
        sudo apt -y install docker.io
    fi

    #TODO Detect version, upgrade
    echo "Install Docker-compose"
    # Docker-compose
    local COMPOSE_VERSION=$(curl -s -o /dev/null -I -w "%{redirect_url}\n" https://github.com/docker/compose/releases/latest | grep -oP "[0-9]+(\.[0-9]+)+$")
    sudo curl -L https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
}

# Init docker in swarm mode if docker installed
# usage: init_docker_swarm
init_docker_swarm() {
    # Check if docker installed
    if ! [[ $(which docker) ]]
    then
        echo "Docker not installed"
        exit 1
    fi

    sudo docker swarm init

    # Todo detect network issues
    #    local ext_ip=$(dig +short myip.opendns.com @resolver1.opendns.com)
    #    sudo docker swarm init --listen-addr ${ext_ip} --advertise-addr ${ext_ip}
}
