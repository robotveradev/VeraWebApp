#!/usr/bin/env bash

# array of volume directories  names to export
declare -a vol_list=("dbdump"
                     "nginx"
                     "static"
                     "media"
                    )

# array of image names to export
declare -a img_list=("vera_main")
# array contain Dockerfile location for image
declare -a img_loc=(
                    ["vera_main"]="."
                   )

# array of files to send
declare -a send_list=("images.tgz"
                      "volumes.tgz"
                      "docker-compose.yml"
                     )

default_path=verajobs
