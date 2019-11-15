####################################
#
#  Dockerfile for Root the Box
#  v0.1.2 - By Moloch, ElJeffe

FROM python:3

RUN mkdir /opt/rtb
ADD . /opt/rtb

RUN apt-get update
RUN apt-get install software-properties-common -y
RUN apt-get update
RUN apt-get install build-essential zlib1g-dev memcached libmemcached-dev -y
RUN apt-get install python3-pycurl sqlite3 libsqlite3-dev -y

ADD ./setup/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt --upgrade

VOLUME ["/opt/rtb/files"]
ENTRYPOINT ["/opt/rtb/rootthebox.py", "--setup=docker", "--sql_dialect=sqlite"]
