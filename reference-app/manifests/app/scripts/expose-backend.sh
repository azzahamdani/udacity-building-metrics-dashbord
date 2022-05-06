#!/bin/bash

kubectl port-forward svc/backend-service --address 0.0.0.0 8080:8081