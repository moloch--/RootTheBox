####################################
#
#  Dockerfile for Root the Box
#  v0.1.1 - By Moloch, ElJeffe

FROM python:3.6

RUN mkdir /opt/rtb
ADD . /opt/rtb
RUN /opt/rtb/setup/depends.sh -y

VOLUME ["/opt/rtb/files"]
ENTRYPOINT ["/opt/rtb/rootthebox.py", "--setup=docker", "--sql_dialect=sqlite"]
