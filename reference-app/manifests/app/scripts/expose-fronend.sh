#!/bin/bash

kubectl port-forward svc/frontend-service --address 0.0.0.0 3111:8080