#!/bin/bash
if [ -z "$1" ]
  then
    echo "You must specify the version of the image being built"
    exit 1
fi
docker build -t registry.b2w.io/b2wdigital/predictionio-b2w:"$1" .


