FROM mysql:latest

USER root
ENV WORK_PATH /usr/local/work
# 创建文件夹
RUN mkdir -p $WORK_PATH
WORKDIR $WORK_PATH
#定义会被容器自动执行的目录
ENV AUTO_RUN_DIR /docker-entrypoint-initdb.d
# 复制文件
COPY ./sql ./sql
COPY ./sql/init_data.sh $AUTO_RUN_DIR
# 增加可执行权限
RUN chmod a+x $AUTO_RUN_DIR/init_data.sh

