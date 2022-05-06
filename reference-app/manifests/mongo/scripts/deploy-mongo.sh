# !/bin/bash

source utils.sh

infoln "deploy CRDs"

kubectl apply -f ../mongodb-crds.yaml
kubectl apply -f ../mongodb-cr.yaml

infoln "deploy, operator , permissions , entreprise"

kubectl apply -f ../mongdb-operator.yaml
kubectl apply -f ../mongodb-enterprise.yaml
kubectl apply -f ../mongodb-perms.yaml