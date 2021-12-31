# 拉取Python官方3.7.9镜像
FROM python:3.7.9-slim

# 创建目录
RUN mkdir -p /var/www/scmproxy

# 设置当前工作目录
WORKDIR /var/www/scmproxy

# 拷贝源码
COPY ./ ./

# 执行环境初始化
RUN pip3 install -U setuptools && \
    pip3 install -r requirements.txt && \
    chmod u+x start.sh

