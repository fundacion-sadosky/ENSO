# Server Data

- ingarue.santafe-conicet.gov.ar
- 172.16.248.200
- fede / 1ng4rE657

## GAMS Vagrant VM

### Service startup

- Start VM
```bash
/home/fede/vms/vagrant up
```
- Open virtualbox
- login as vagrant
- run in desktop `start-gams-api.bat`
- press X and set `Continue running in background`

### Test api

API is running on `http://ingarue.santafe-conicet.gov.ar/gamsapi`

### Service stop

```bash
/home/fede/vms/vagrant halt
```

## Run in DEV Mode in server

```bash
cd /home/fede/dev/pue-platform/docker
docker compose -f ./docker-compose-srv.yml up -d
```

- Test DEV NGINX service: `http://172.16.248.200`
- Test DEV Minio service: `http://172.16.248.200:9001/`
Required buckets: `platform-images`, `platform-docs`
- Test DEV MongoDB: `mongodb://rootuser:rootpass@172.16.248.200:27017/?authSource=admin&readPreference=primary&directConnection=true&ssl=false`

### Start apps in dev mode

```bash
/home/fede/dev/pue-platform/run-everything-srv.sh
```

### Monitor apps in dev mode

- `ps aux | grep 'hopeit\|pue-platform'`

### Stop apps in dev mode

- `kill -9 ID` :)

### Access & 1st time setup

- http://172.16.248.200/
- 1st time setup: http://172.16.248.200:8021/api/docs
- http://ingarue.santafe-conicet.gov.ar:8021/api/docs
- http://ingarue.santafe-conicet.gov.ar:8022/api/docs
- http://ingarue.santafe-conicet.gov.ar/api/admin/docs/


cd /home/fede/dev/pue-platform/docker
docker compose -f docker-compose-srv.yml up
or
docker compose -f docker-compose-srv.yml up -d

docker compose -f docker-compose-srv.yml down


cd /home/fede/vms/
vagrant up
virtualbox


cd /home/fede/dev/pue-platform/infrastructure/pue-srv-dev
./run-everything-srv.sh


watch 'ps aux | grep hopeit.server'
watch 'ps aux | grep vite'
watch 'ps aux | grep pue-platform'


superuser / dire

http://ingarue.santafe-conicet.gov.ar:8021/api/docs/
http://ingarue.santafe-conicet.gov.ar/admin

## Minikube K8s server implementation


### Userfull commands

- minikube start --driver docker
- minikube stop
- minikube pause
- minikube unpause
- minikube addons list
- minikube logs

- kubectl get po -A
- kubectl describe pod podname -n namespace
- watch kubectl get pods
- kubectl get svc -o wide
- kubectl get endopoints

investigar mejor esto
- kubectl port-forward pod/minio 9000 9000

### Testing installation

- Open dashboard (not remote)
```bash
minikube dashboard
```
```bash
minikube dashboard --url
```

### Demo deploy to minikube

- first create config and secret

kubectl apply -f mongo-config.yaml
configmap/... created

kubectl apply -f mongo-secret.yaml
secret/... created

kubectl apply -f mongo.yaml
deployment.apps/... created
service/... created

kubectl get all
kubectl get configmap
kubectl get secret
kubectl get pods
kubectl get svc

kubectl --help
kubectl describe pod component
kubectl logs name_of_pod -f

kubectx
kubens
kube ctx
kube ns

minikube addons enable ingress

### Helm (https://helm.sh/docs/intro/install/)

- helm charts
- bundle stacks for kubernetes
- templating engine

helm search keyword
helm install chartname



### Setup Ingress with Minikube

- enable
```bash
minikube addons enable ingress
```

- test if working
```bash
kubectl get pods -n ingress-nginx

NAME                                        READY   STATUS      RESTARTS    AGE
ingress-nginx-admission-create-g9g49        0/1     Completed   0          11m
ingress-nginx-admission-patch-rqp78         0/1     Completed   1          11m
ingress-nginx-controller-59b45fb494-26npt   1/1     Running     0          11m
```

### Setup Ingress Controller ?
First add the service to the cluster

Installing metrics-server

    In a lot of places, this is done with a little bit of custom YAML

    (derived from the official installation instructions)

    We're going to use Helm one more time:

    helm upgrade --install metrics-server bitnami/metrics-server \
      --create-namespace --namespace metrics-server \
      --set apiService.create=true \
      --set extraArgs.kubelet-insecure-tls=true \
      --set extraArgs.kubelet-preferred-address-types=InternalIP

### Installing cert-manager

    It can be installed with a YAML manifest, or with Helm

    Let's install the cert-manager Helm chart with this one-liner:

    helm install cert-manager cert-manager \
        --repo https://charts.jetstack.io \
        --create-namespace --namespace cert-manager \
        --set installCRDs=true

### Ingress:

Install Ingress:

```
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update
helm install --namespace default ingress-nginx ingress-nginx/ingress-nginx
```

```
kubectl --namespace pue-stage get services -o wide -w ingress-nginx-controller
```

```
$ cd ingress
$ kubectl apply -f .
```


k8s/cert-manager.md
176/233

### Generate secret

To generate a secret from text
```bash
echo -n "Text to encode" | base64
```

To generate a secret from file
```bash
cat file.ext | base64
```

### docker registry private access

- Go to Gitlab Deploy tokens and generate a new token with read_registry permission
- Set user and token password in /docker_registry/create_registry.sh
- run /docker_registry/create_registry.sh
- run `kubectl get secret registry-key -o yaml`
- put results in `00-registry-key.yaml

## Setup process

Go to files folder:
```bash
cd /home/fede/dev/pue-platform/infrastructure/pue-stage
```

Apply in order:

```bash
kubectl apply -f 00-ns-pue-stage.yaml
kubectl apply -f 00-registry-key.yaml
kubectl apply -f 01-private-keys-secrets.yaml
kubectl apply -f 01-public-keys-secrets.yaml
kubectl apply -f 02-pv-redis.yaml
kubectl apply -f 03-redis-pvc.yaml
kubectl apply -f 03-redis.yaml

kubectl apply -f 02-pv-res.yaml
kubectl apply -f 04-minio-config-map.yaml
kubectl apply -f 04-minio-pvc.yaml
kubectl apply -f 04-minio1.yaml
kubectl apply -f 04-minio2.yaml
kubectl apply -f 04-minio.yaml
kubectl apply -f 04z-minio-createbuckets.yaml

kubectl apply -f 02-pv-mongodb.yaml
kubectl apply -f 05-mongodb-config-map.yaml
kubectl apply -f 05-mongodb-pvc.yaml
kubectl apply -f 05-mongodb.yaml

kubectl apply -f 10-api-gateway-config-map0.yaml
kubectl apply -f 10-api-gateway-config-map1.yaml
e kubectl apply -f 10-api-gateway.yaml

kubectl apply -f 02-pv-sec.yaml
kubectl apply -f 11-app0-admin-api-pvc.yaml
kubectl apply -f 11-app0-admin-api.yaml

kubectl apply -f 12-app0-admin-ui.yaml
kubectl apply -f 13-app0-app1-api.yaml
kubectl apply -f 14-app0-app1-ui.yaml

```


