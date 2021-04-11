#!/usr/bin/env bash

usage() {
  echo "start_squall.sh -e"
  echo "-e export logs"
  exit 0
}
while getopts :eh opts
do
    case "${opts}" in
        e) export_logs="true";;
        h) usage;;
    esac
done

if [ "$export_logs" == "true" ]; then
  kubectl apply -f metricbeat-kubernetes.yaml
  kubectl apply -f filebeat-kubernetes.yaml
fi

kubectl apply -f squall.yaml

kubectl get pods -n kube-system
kubectl get pods -n default