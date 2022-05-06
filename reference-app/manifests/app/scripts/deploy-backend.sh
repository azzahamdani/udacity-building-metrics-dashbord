#!/bin/bash

source utils.sh

infoln "deploy backend"

kubectl apply -f ../backend-deployment.yaml

infoln "view backend"

kubectl get pods 