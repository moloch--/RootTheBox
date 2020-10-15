####################################
#
#  Dockerfile for Root the Box
#  v0.1.3 - By Moloch, ElJeffe

FROM python:3.8

RUN mkdir /opt/rtb
ADD . /opt/rtb

RUN apt-get update
RUN apt-get install build-essential zlib1g-dev -y
RUN apt-get install python3-pycurl sqlite3 libsqlite3-dev -y

ADD ./setup/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt --upgrade

VOLUME ["/opt/rtb/files"]
ENTRYPOINT ["python3", "/opt/rtb/rootthebox.py", "--setup=docker", "--sql_dialect=sqlite"]
