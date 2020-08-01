#!/bin/bash

# force DB initialization

ROOT_DIR=$(cd $(dirname $0)/..; pwd)
DB_DIR="$ROOT_DIR/db"

MYSQL_DATABASE=app
MYSQL_USER=isucon
MYSQL_PASSWORD=nocusi
MYSQL_HOST=localhost

mysql -h $MYSQL_HOST -u$MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE -e "DROP DATABASE IF EXISTS $MYSQL_DATABASE; CREATE DATABASE $MYSQL_DATABASE;"
mysql -h $MYSQL_HOST -u$MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE < "$DB_DIR/init.sql"
if [[ -f "$DB_DIR/seed.sql" ]]; then
        mysql -h $MYSQL_HOST -u$MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE < "$DB_DIR/seed.sql"
fi
