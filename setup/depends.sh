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

# #########################
#     value
# #########################
current_path="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

if [[ "$EUID" != "0" ]]; then
  echo "[!] This script must be run as root." 1>&2
  exit 1
fi

# -y flag will be passed to this variable for a non-interactive setup.
SKIP=""

while getopts "y" OPTION; do
  case $OPTION in
    y)
      SKIP=" -y"
      ;;
  esac
done

if [[ "$SKIP" == " -y" ]]; then
  echo "[*] Non-interactive setup - Setting mysql password to 'your_password'"
  sudo debconf-set-selections <<< 'mysql-server mysql-server/root_password password your_password'
  sudo debconf-set-selections <<< 'mysql-server mysql-server/root_password_again password your_password'
fi

if [[ $OSTYPE == "linux-gnu" ]]; then
  echo -e "\t#########################"
  echo -e "\t   Linux Configuration"
  echo -e "\t#########################"

  echo "[*] Add Universe Repo..."
  add-apt-repository universe "$SKIP"
  apt-get update

  echo "[*] Installing pip/gcc..."
  apt-get install python-pip python-dev build-essential "$SKIP"

  echo "[*] Installing packages..."
  apt-get install mysql-server memcached libmemcached-dev python-mysqldb python-mysqldb-dbg python-pycurl python-recaptcha zlib1g-dev default-libmysqlclient-dev "$SKIP"

elif [[ ${OSTYPE} == "darwin14" ]]; then
  echo -e "\t#########################"
  echo -e "\t   OSX Configuration"
  echo -e "\t#########################"
  # Check if homebrew is installed
  if test ! "$(which brew)"; then
    echo "Installing homebrew..."
    ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
  fi

  # Update homebrew recipes
  echo "Update homebrew..."
  brew update

  echo "Brew install package..."
  brew install python mysql memcached libmemcached zlib	

fi	

echo "[*] Installing python libs..."

#sh "$current_path/python-depends.sh"
python_version="$(python -c 'import platform; major, minor, patch = platform.python_version_tuple(); print(major);')"
if [[ "$python_version" == "2" ]]; then
    pip2 install -r "$current_path/requirements.txt" --upgrade
else
    pip3 install -r "$current_path/requirements.txt" --upgrade
fi

echo ""
echo "[*] Setup Completed."
