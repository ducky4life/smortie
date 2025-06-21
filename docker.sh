#!/bin/bash

git pull
docker build -t smortie:latest -f Dockerfile .
docker run --rm --name smortie smortie:latest
