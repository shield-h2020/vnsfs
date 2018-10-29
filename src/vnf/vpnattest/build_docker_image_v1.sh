#!/bin/bash
# This command is run on the VIM-emulator machine to prepare the image for the
# VNSF in the local Docker catalogue
docker build -t vnf:v1 -f Dockerfile.v1 .
