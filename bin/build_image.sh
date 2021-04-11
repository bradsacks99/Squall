#!/bin/bash

cd $SQUALL_HOME

docker build -t bsacks99/squall .
docker push bsacks99/squall:latest
