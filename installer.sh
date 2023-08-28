#!/bin/bash
if command -v python > /dev/null 2>&1; then
  TMP_FILE=/tmp/botengine.tmp
  TMP_FILE_ONE=/tmp/botengine_bytecode.tmp
  pip install requests python-dateutil tzlocal dill
  if [ -e /tmp/botengine.tmp ]; then
    echo "Cleaning up from previous install failure"
    rm -f /tmp/botengine.tmp
  fi
  if [ -e /tmp/botengine_bytecode.tmp ]; then
    echo "Cleaning up from previous install failure"
    rm -f /tmp/botengine_bytecode.tmp
  fi
  echo "Fetching latest version ..."
  curl --progress-bar https://raw.githubusercontent.com/caredailyai/botlab/master/botengine -o /tmp/botengine.tmp
  curl --progress-bar https://raw.githubusercontent.com/caredailyai/botlab/master/botengine_bytecode -o /tmp/botengine_bytecode.tmp
  if [ ! -d /usr/local/bin ]; then
    echo "Making /usr/local/bin"
    mkdir -p /usr/local/bin
  fi
  echo "Installing ..."
  sudo mv /tmp/botengine.tmp /usr/local/bin/botengine
  sudo mv /tmp/botengine_bytecode.tmp /usr/local/bin/botengine_bytecode
  chmod 755 /usr/local/bin/botengine
else
  echo "Please download Python 2.7, then run this file again"
fi
