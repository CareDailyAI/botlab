#!/bin/bash

find ./ -name "*.py" -exec pylint -E '{}' \; | grep -v "'_'"

