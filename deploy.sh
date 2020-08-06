#!/bin/bash -x

# nginx
sudo cp infra/etc/nginx/nginx.conf /etc/nginx/nginx.conf
sudo cp infra/etc/nginx/niita /etc/nginx/sites-enabled/niita

# mysql
sudo cp infra/etc/mysql/mysql.conf.d/mysqld.cnf /etc/mysql/mysql.conf.d/mysqld.cnf

# log-lotate and restart services
./pre_bench.sh
