## Clone the repository
```
git clone git@github.com:my-repo.git'
cd my-repo
```

# Deploy project to server
First ensure you got ssh access to your remote server where project will be running
To deploy project use sendto.sh script
```
./sendto.sh <remotehost>
For example
./sendto.sh root@123.123.123.1
```

By default project will be copied into /opt/<project name>
If for some reason <projectname> directory not exists, or was created as file you should delete it and create manually. Then run send script again.

# Deploying
## Prepare server
Go into project directory
```
cd /opt/<projectname>
```

If its your first deploy you need to setup server. Go into you project directory
And run init server script
```
./server.sh init
```
Script will create swapfile, upgrade os and install docker
If you project use swarm mode use -swarm key

## Deploy
Before deploying project ensure you have been copied secrets directory into project directory.
Then run deployment script
```
./server.sh deploy
```
Note: any env, secrets or ssl files must be copied to server manually

## Run project
if your project is standalone, then all you need is to run script providing service name.

WARNING: you should copy secrets directory manually in project directory if required!
```
./server.sh run <servicename>
```
You can use any name you want. It will be saved for future operations.
 
## Update existing running project
Update process is the same as deploying process. The only exception is command. Use update instead run
```
./server.sh update
```

## Stop project
If you need to stop some project go to <projectname> directory and run stop command
```
./server.sh stop
```

# Examples
## vera.wtf
```
./sendto.sh root@hostip
ssh root@hostip
cd /opt/verajobs
./server.sh init
./server.sh deploy
./server.sh run vrjbs
```
