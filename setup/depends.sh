#!/bin/bash

#    Copyright 2012 Root the Box
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

if [ "$(id -u)" != "0" ]; then
	echo "[!] This script must be run as root." 1>&2
	exit 1
fi

echo "[*] Installing pip/gcc ..."
apt-get install python-pip python-dev build-essential

echo "[*] Installing packages ..."
apt-get install mysql-server memcached libmemcached-dev python-mysqldb python-mysqldb-dbg python-pycurl python-recaptcha

echo "[*] Installing python libs ..."

if [ -f /usr/local/bin/pip ]
  then
    pip_path="/usr/local/bin/pip"
else
	pip_path="/usr/bin/pip"
fi
$pip_path install --upgrade pip
$pip_path install --upgrade virtualenv
$pip_path install tornado
$pip_path install scrypt
$pip_path install sqlalchemy
$pip_path install pylibmc
echo ""
echo "[*] Setup Completed."
