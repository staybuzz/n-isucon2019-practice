#!/bin/bash -x
# from: https://gist.github.com/asflash8/0cbb743fd23385f32b412c908959a032
set -ex

sudo chmod 777 /var/log/mysql
if [ -f /var/log/mysql/mysql-slow.log ]; then
    sudo mv /var/log/mysql/mysql-slow.log /var/log/mysql/mysql-slow.log.$(date "+%Y%m%d_%H%M%S")
fi
if [ -f /var/log/nginx/access.log ]; then
    sudo mv /var/log/nginx/access.log /var/log/nginx/access.log.$(date "+%Y%m%d_%H%M%S")
fi
if [ -f /tmp/lineprof.log ]; then
    sudo mv /tmp/lineprof.log /tmp/lineprof.log.$(date "+%Y%m%d_%H%M%S")
fi
sudo systemctl restart mysql
sudo systemctl restart niita_python
sudo systemctl restart nginx
