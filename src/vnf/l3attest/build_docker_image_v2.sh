#!/bin/bash
# This command is run on the VIM-emulator machine to prepare the image for the
# VNSF in the local Docker catalogue
docker build -t vnf:v2 -f Dockerfile.v2 .
