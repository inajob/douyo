FROM debian:latest

MAINTAINER ina

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update; \
    apt-get -y upgrade; \
    apt-get -y dist-upgrade; \
    apt-get -y install python python-beautifulsoup mecab-ipadic-utf8 python-crypto nginx curl python-pip; \
    apt-get clean; \
    rm -rf /var/lib/apt/lists/*

RUN echo "Asia/Tokyo" > /etc/timezone
RUN dpkg-reconfigure tzdata
RUN pip install pymecab==1.0.4

COPY nginx.conf /etc/nginx/sites-enabled/default

COPY app /app

RUN chmod 755 /app/bat/digzon.sh

RUN ln -sf /dev/stdout /var/log/nginx/access.log \
	&& ln -sf /dev/stderr /var/log/nginx/error.log

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

