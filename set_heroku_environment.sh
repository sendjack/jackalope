#!/bin/sh

# ./script.sh REMOTE_NAME CONFIG_FILE
# 
# Example
# ./set_heroku_environment.sh staging .staging.env

if (( $# == 2 ))
then
    FIELDS=$(cat $2 | sed '/^\#/d' | sed '/^$/d' | tr '\n' ' ')
    ENVIRONMENT=$1
    heroku config:set $FIELDS --remote $ENVIRONMENT
else
    echo "Arg1: App, Arg2: env file"
fi
