#!/bin/bash

git pull
cd playlists
git pull
cd ..
docker stop smortie
docker build -t smortie:latest -f Dockerfile .
docker run --rm --name smortie smortie:latest
