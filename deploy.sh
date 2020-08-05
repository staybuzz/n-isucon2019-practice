#!/bin/bash -x

# nginx
sudo cp infra/etc/nginx/nginx.conf /etc/nginx/nginx.conf

# mysql
sudo cp infra/etc/mysql/mysql.conf.d/mysqld.cnf /etc/mysql/mysql.conf.d/mysqld.cnf

# log-lotate and restart services
./pre_bench.sh
