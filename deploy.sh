#!/bin/bash -x

# kernel params
sudo cp infra/sysctl.conf /etc/sysctl.conf
sudo sysctl -p

# nginx
sudo cp infra/etc/nginx/nginx.conf /etc/nginx/nginx.conf
sudo cp infra/etc/nginx/niita /etc/nginx/sites-enabled/niita

# mysql
sudo cp infra/etc/mysql/mysql.conf.d/mysqld.cnf /etc/mysql/mysql.conf.d/mysqld.cnf

# pip
pip3.7 install -r python/requirements.txt

# log-lotate and restart services
./pre_bench.sh

