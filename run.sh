#! /bin/bash

#SECRET_KEY=
# 服务器绑定二级域名 端口 和过滤IP地址设置
#WEBSERVER_HOST=
WEBSERVER_PORT=8080
WEBSERVER_ACCESSIP=127.0.0.1
# 注册发送邮件服务器
#MAIL_SERVER=
#MAIL_SERVERPORT=
#MAIL_USERNAME=
#MAIL_PASSWORD=
#MAIL_ADDR=
# data url
#DEV_DATABASE_URL=
#TEST_DATABASE_URL=
#DATABASE_URL=

python manage.py config
if [ -f "*-nginx.conf" ]; then
    echo "generate nginx conf failed!"
    exit 0
fi
echo "generate nginx conf success!"
if [ -f "*-uwsgi.xml" ]; then
    echo "generate uwsgi conf failed!"
    exit 0
fi
echo "generate uwsgi conf success!"
cp *-nginx.conf /etc/nginx/conf.d/
echo "migrate nginx conf to /etc/nginx/conf.d/....."
/usr/sbin/nginx -s reload
echo "reload nginx....."
uwsgi -x *-uwsgi.xml
echo "success load uwsgi!!!"
