#!/bin/bash

TMP_FILE=/tmp/composer.tmp
if [ -e /tmp/composer.tmp ]; then
  echo "Cleaning up from previous install failure"
  rm -f /tmp/composer.tmp
fi
echo "Fetching latest version ..."
curl --progress-bar http://www.peoplepowerco.com -o /tmp/composer.tmp
if [ ! -d /usr/local/bin ]; then
  echo "Making /usr/local/bin"
  mkdir -p /usr/local/bin
fi
echo "Installing ..."
sudo mv /tmp/composer.tmp /usr/local/bin/composer
chmod 755 /usr/local/bin/composer
