#!/bin/sh

FIELDS=$(cat .env .env-prod | sed '/^\#/d' | sed '/^$/d' | tr '\n' ' ')
heroku config:set $FIELDS
