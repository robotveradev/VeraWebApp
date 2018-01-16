# VeraOracle jobBoard

# Installation
Start from clean Ubuntu 16 LTS installation

If your system has no swap partition you should make swap file to avoid low memory conditions

```sh
dd if=/dev/zero of=/swapfile bs=1M count=2000
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo "/swapfile   none    swap    sw    0   0" >> /etc/fstab
```

Upgrade packages and grub

```
echo -e "LC_ALL=en_US.UTF-8\nLANG=en_US.UTF-8" >> /etc/environment
read -d "" UPGRADESCRIPT <<"EOF"
export DEBIAN_FRONTEND=noninteractive
apt purge -y grub-pc grub-common
apt autoremove -y 
rm -rf /etc/grub.d/
sudo add-apt-repository ppa:ethereum/ethereum
apt -y update
apt upgrade -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" 
apt install -y git solc libssl-dev openssl screen vim python3-pip python3-venv mc nginx supervisor libjpeg-dev
service supervisor restart  
apt install -y grub-pc grub-common
grub-install /dev/vda
update-grub
EOF
echo "$UPGRADESCRIPT" > /tmp/upgradescript
bash /tmp/upgradescript
```

and

```sh
reboot
```

```
Install python virtualenv, create configs, clone project from git and apply some patches

```sh
cd /opt
mkdir vera_jobboard
cd vera_jobboard
mkdir logs static media configs
python3 -m venv env
cd configs

#
#set config for gunicorn
read -d "" VRJB<<"EOF"
#!/bin/sh

NAME="veraOracleJobBoard"
DJANGODIR=/opt/vera_jobboard/RobotVeraWebApp/
USER=root
GROUP=root
NUM_WORKERS=2                                    
DJANGO_SETTINGS_MODULE=vera.settings            
DJANGO_WSGI_MODULE=vera.wsgi                     
echo "Starting $NAME as `whoami`"
cd $DJANGODIR
source ../env/bin/activate
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH
RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR
exec ../env/bin/gunicorn ${DJANGO_WSGI_MODULE}:application \
  --name $NAME \
  --workers $NUM_WORKERS \
  --user=$USER --group=$GROUP \
  --bind="127.0.0.1:9023" \
  --log-level=debug \
  --log-file=-
EOF
echo "$VRJB" > /opt/vera_jobboard/configs/veraOracleJobBoard
chmod u+x /opt/vera_jobboard/configs/veraOracleJobBoard

#
#set config for nginx
read -d "" NGINX <<"EOF"
server {
    listen 80;
    server_name 127.0.0.1 vera-job.pro www.vera-job.pro;
    access_log  /opt/vera_jobboard/logs/nginx_access.log;

    location /media  {
        alias /opt/vera_jobboard/media;
        expires 30d;
        add_header Pragma public;
        add_header Cache-Control "public";
    }
    location /static {
        alias /opt/vera_jobboard/static;
        expires 30d;
        add_header Pragma public;
        add_header Cache-Control "public";
    }

    location / {
        proxy_pass http://127.0.0.1:9023;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_connect_timeout       600;
        proxy_send_timeout          600;
        proxy_read_timeout          600;
        send_timeout                600;
    }
  }
EOF
echo "$NGINX" > /opt/vera_jobboard/configs/nginx.conf

#
#set config for supervisor
read -d "" VISOR <<"EOF"
[program:veraOracleJobBoard_web]
command = /opt/vera_jobboard/configs/veraOracleJobBoard
user = root
stdout_logfile = /opt/vera_jobboard/logs/gunicorn_supervisor.log
redirect_stderr = true
environment=LANG=en_US.UTF-8,LC_ALL=en_US.UTF-8
EOF
echo "$VISOR" > /opt/vera_jobboard/configs/supervisor.conf

cd /opt/vera_jobboard
source /opt/vera_jobboard/env/bin/activate
pip install --upgrade pip setuptools wheel
git clone https://github.com/achievement008/RobotVeraWebApp.git
cd RobotVeraWebApp
pip install gunicorn==19.6.0
pip install -r requirements.txt



```

set databases and mocks

```sh

#
# Migrate
./manage.py migrate
#
#
# Add users
read -d "" PYCODE <<"EOF"
from django.contrib.auth.models import User
user = User.objects.create_user(username='kirill',
                                 email='kirill@ongrid.pro',
                                 password='kirill')
EOF
echo "$PYCODE" | ./manage.py shell
ln -s /opt/vera_jobboard/configs/supervisor.conf /etc/supervisor/conf.d/veraOracleJobBoard.conf
ln -s /opt/vera_jobboard/configs/nginx.conf /etc/nginx/sites-enabled/vera_jobboard.conf
supervisorctl update
supervisorctl restart all
./manage.py collectstatic --noinput
```

Install testrpc and deploy contracts

```sh

curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.33.6/install.sh | bash
exec bash
nvm install node
npm install -g ethereumjs-testrpc

read -d "" RCLOCAL <<"EOF"
#!/bin/bash
cd /opt/vera_jobboard
source ./env/bin/activate

read -d "" PYCODE <<"EOF"
from jobboard.models import Employer, Candidate
Employer.objects.all().delete()
Candidate.objects.all().delete()
EOF
echo "$PYCODE" | ./manage.py shell

screen -dmS vera_jobboard bash -c 'testrpc'
exit 0
python RobotVeraWebApp/deploy_contract.py
EOF
echo "$RCLOCAL" > /etc/rc.local
#
```

reboot and have fun!