#!/bin/bash

if [ "$(id -u)" != "0" ]; then
	echo "This script must be run as root." 1>&2
	exit 1
fi

echo "Installing pip ..."
apt-get install python-pip python-dev build-essential && 
pip install --upgrade pip &&
pip install --upgrade virtualenv

echo "Installing packages ..."
apt-get install python-mysqldb python-mysqldb-dbg python-recaptcha python-jsonpickle

echo "Installing tornado/sqlalchemy ..."
/usr/local/bin/pip install tornado
/usr/local/bin/pip install sqlalchemy

