#!/usr/bin/env bash

kubectl create secret docker-registry squall-registry --docker-server=docker.io --docker-username=$DOCKER_USERNAME --docker-password=$DOCKER_TOKEN --docker-email=$DOCKER_EMAIL
