#!/bin/bash -ex
docker run --rm -d -v src/main -p 0.0.0.0:8279:8279 treasury-orders:latest