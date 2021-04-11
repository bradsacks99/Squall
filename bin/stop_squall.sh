#!/usr/bin/env bash

kubectl delete -f metricbeat-kubernetes.yaml
kubectl delete -f filebeat-kubernetes.yaml
kubectl delete -f squall.yaml

kubectl get pods -n kube-system
kubectl get pods -n default