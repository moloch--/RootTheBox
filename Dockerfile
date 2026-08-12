####################################
#
#  Dockerfile for Root the Box
#  v0.1.3 - By Moloch, ElJeffe

FROM python:3.8

RUN mkdir /opt/rtb
#########################
# temporary uncomment for dev
# ADD . /opt/rtb

RUN apt-get update && apt-get install -y \
build-essential zlib1g-dev rustc \
python3-pycurl sqlite3 libsqlite3-dev 

ADD ./setup/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt --upgrade

ENV SQL_DIALECT=sqlite


#########################
# temporary cahnge for dev
# VOLUME ["/opt/rtb/files"] -> VOLUME ["/opt/rtb"]
VOLUME ["/opt/rtb"]
ENTRYPOINT ["python3", "/opt/rtb/rootthebox.py", "--setup=docker"]
