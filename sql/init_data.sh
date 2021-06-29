#!/bin/bash
echo "Now will create DataBase,HT,HT_test, API"
WORK_PATH="."
mysql -uroot -p$MYSQL_ROOT_PASSWORD <<EOF
source $WORK_PATH/sql/create_db.sql
EOF
echo ""
echo ""
echo "============================================="
echo "now will create table"
for file in $(ls $WORK_PATH/sql/create)
do
  echo "exec create" $WORK_PATH/sql/create/$file
  mysql -uroot -p$MYSQL_ROOT_PASSWORD <<EOF
  source $WORK_PATH/sql/create/$file
EOF
echo ""
done
echo ""
echo ""
echo "============================================="
echo "now will insert data, It's May take some time"
for file in $(ls $WORK_PATH/sql/insert)
do
  echo "exec insert" $WORK_PATH/sql/insert/$file
  mysql -uroot -p$MYSQL_ROOT_PASSWORD <<EOF
  SET autocommit=0 ; source $WORK_PATH/sql/insert/$file; COMMIT ;
EOF
echo ""
done
