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
	echo "===> get libs in $folder..."
	cd $folder
	rm -rf node_modules
	rm package-lock.json
	npm install --legacy-peer-deps
	echo "===> get libs $folder OK"
	sleep 3
	cd ..
done
