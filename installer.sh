#!/bin/bash
if command -v python3 > /dev/null 2>&1; then
  echo true
  TMP_FILE=/tmp/composer.tmp
  TMP_FILE_ONE=/tmp/composer_bytecode.tmp
  pip3 install requests python-dateutil tzlocal dill
  if [ -e /tmp/composer.tmp ]; then
    echo "Cleaning up from previous install failure"
    rm -f /tmp/composer.tmp
  fi
  if [ -e /tmp/composer_bytecode.tmp ]; then
    echo "Cleaning up from previous install failure"
    rm -f /tmp/composer_bytecode.tmp
  fi
  echo "Fetching latest version ..."
  curl --progress-bar https://raw.githubusercontent.com/peoplepower/composer-sdk-python/master/composer -o /tmp/composer.tmp
  curl --progress-bar https://raw.githubusercontent.com/peoplepower/composer-sdk-python/master/composer_bytecode -o /tmp/composer_bytecode.tmp
  if [ ! -d /usr/local/bin ]; then
    echo "Making /usr/local/bin"
    mkdir -p /usr/local/bin
  fi
  echo "Installing ..."
  sudo mv /tmp/composer.tmp /usr/local/bin/composer
  sudo mv /tmp/composer_bytecode.tmp /usr/local/bin/composer_bytecode
  chmod 755 /usr/local/bin/composer
else
  echo "Please download Python 3, then run this file again"
fi
