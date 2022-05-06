#!/bin/bash

source utils.sh

infoln "deploy fronend"

kubectl apply -f ../frontend-deployment.yaml

infoln "view frontend"

kubectl get pods 