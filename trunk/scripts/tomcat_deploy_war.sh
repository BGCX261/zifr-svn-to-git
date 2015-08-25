#!/bin/sh
#----------------------------------------------------------------
# tomcat_deploy_war - deploy a .war file to tomcat webapps 
#
# This script will do a 'clean' install of a .war file -- i.e.,
# it will first purge the existing application after stopping
# Tomcat.
# 
# It then copies the specified .war file to $TOMCAT_HOME/
# webapps before starting Tomcat again. 
#
# When Tomcat restarts, it will automatically  extract all 
# files from the newly copied war file into a subdirectory 
# of the same name.
#
# The TOMCAT_HOME environment variable must be defined.
#
# Depending on your configuration, you may have to run this
# script as superuser.  For example:
#
#   su root tomcat_deploy_war mywebapp.war 
#
# Version: 0.5  30-Jul-01   Initial version
#
# Copyright (C) 2001 Reed Esau (reed.esau@pobox.com)
# The author requires that any copies or derived works include 
# this copyright notice; no other restrictions are placed on 
# its use.  Use this script at your own risk.
#----------------------------------------------------------------

if [ -z "$1" ]; then
	echo "You must specify a '.war' file to deploy"
	exit 10
fi

if [ -z "$TOMCAT_HOME" ]; then
	echo "TOMCAT_HOME must be defined"
	exit 20
fi

if [ ! -d "$TOMCAT_HOME" ]; then
	echo "$TOMCAT_HOME is not a valid directory"
	exit 21
fi

if [ ! -r "$1" ]; then
	echo "The file $1 does not exist or isn't readable"
	exit 30
fi

# strip off the directory and .war file extension
APP=`basename $1 .war` 
APPDIR="$TOMCAT_HOME/webapps/$APP"

if [ "$1" -ot "$APPDIR.war" ]; then
	echo "The file $1 is older than the $APPDIR.war.  Nothing done." 
	exit 40
fi

# start the process

echo "Deploying $1 to $APPDIR.  Shutting down Tomcat..."

$TOMCAT_HOME/bin/shutdown.sh

sleep 2

if [ -d "$APPDIR" ]; then
	rm -fr "$APPDIR"
fi

if [ "$1" != "$APPDIR.war" ]; then
	cp -p "$1" "$TOMCAT_HOME/webapps"
fi

$TOMCAT_HOME/bin/startup.sh

sleep 5

echo "Done."

#eof
