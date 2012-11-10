#!/bin/sh

if (( $# == 2 ))
then
    FIELDS=$(cat $2 | sed '/^\#/d' | sed '/^$/d' | tr '\n' ' ')
    ENVIRONMENT=$1
    heroku config:set $FIELDS --remote $ENVIRONMENT
else
    echo "Arg1: App, Arg2: env file"
fi
