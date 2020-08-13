#!/bin/bash

# initialize db for scoring

ROOT_DIR=$(cd $(dirname $0)/..; pwd)
DB_DIR="$ROOT_DIR/db"

MYSQL_DATABASE=app
MYSQL_USER=isucon
MYSQL_PASSWORD=nocusi
MYSQL_HOST=localhost

# delete except initial data
mysql -h $MYSQL_HOST -u$MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE -e "DELETE FROM users WHERE id > 10000"
mysql -h $MYSQL_HOST -u$MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE -e "DELETE FROM icon WHERE id > 10000"
mysql -h $MYSQL_HOST -u$MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE -e "DELETE FROM items WHERE id > 20000"
mysql -h $MYSQL_HOST -u$MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE -e "DELETE FROM comments WHERE id > 10081"

# index
mysql -h $MYSQL_HOST -u$MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE -e "alter table users ADD INDEX username_idx(username(255));"
mysql -h $MYSQL_HOST -u$MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE -e "alter table items ADD INDEX likes_count_idx(likes_count); "
mysql -h $MYSQL_HOST -u$MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE -e "alter table items ADD INDEX created_at_idx(created_at); "
