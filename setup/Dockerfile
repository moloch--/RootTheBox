FROM ubuntu:14.04
LABEL maintainer="moloch"

 # Update the OS repos
RUN apt-get update && apt-get install -y git build-essentail python python-dev python-pip libmemcached-dev zlib1g-dev libmysqlclient-dev

 # Python dependancies
RUN pip install tornado pbkdf2 mysql-python sqlalchemy python-memcached defusedxml netaddr nose future

 # Download the latest code
WORKDIR /opt
RUN git clone https://github.com/moloch--/RootTheBox
WORKDIR /opt/RootTheBox

 # Setup Application