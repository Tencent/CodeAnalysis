FROM nginx:1.13.7

RUN apt-get update && apt-get install -y unzip procps && rm /etc/nginx/conf.d/default.conf

COPY tca-deploy-source /data/tca-deploy-source

WORKDIR /data/tca-deploy-source/
 
