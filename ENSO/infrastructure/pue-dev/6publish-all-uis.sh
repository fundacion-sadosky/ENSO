#!/bin/bash
clear

echo "===> PUE Platform creating ui DEV ENVS..."
cd /home/fede/dev/lab/pue-platform

# lanzar los frontends
uifolders=(app0-admin-ui \
		   app0-app1-ui \
		   app0-app2-ui \
		   app0-app3-ui \
		   app0-app4-ui \
		   app0-app5-ui \
		   app0-app6-ui \
		  ) 
for folder in ${uifolders[@]}; do
	echo "===> creating publishing $folder..."
	cd $folder
	make build-docker publish-docker
	echo "===> creating publishing $folder OK"
	sleep 3
	cd ..
done
