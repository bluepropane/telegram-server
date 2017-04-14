#!/bin/bash

# TELEGRAM SERVER (telegram-server)
# setup script to install dependencies and configure environment


stringContains () { [ -z "${2##*$1*}" ]; }

# check if we have python3 installed first
REQUIRED_PYTHON3_VERSION=3.6
PYTHON3_VERSION=`python3 --version`
if [ "$?" == "127" ] || ! stringContains "${REQUIRED_PYTHON3_VERSION}" "${PYTHON3_VERSION}" ; then
	# no py3
	echo "Could not locate Python ${REQUIRED_PYTHON3_VERSION}"
	echo "Python >= ${REQUIRED_PYTHON3_VERSION} has to be installed to proceed. Install Python ${REQUIRED_PYTHON3_VERSION} on this machine? (y/n):"
	read INSTALL_PYTHON
	if [ "${INSTALL_PYTHON}" == "yes" ]; then
		# install py3
		sudo apt-get install python${REQUIRED_PYTHON3_VERSION}
	else
		echo 'Aborting setup'
		exit 1
	fi
fi

echo 'Starting setup...'
mkdir creds