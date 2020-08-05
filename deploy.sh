#!/bin/bash -x

# nginx
sudo cp infra/etc/nginx/nginx.conf /etc/nginx/nginx.conf

# log-lotate and restart services
./pre_bench.sh
