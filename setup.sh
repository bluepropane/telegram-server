#!/bin/bash

# TELEGRAM SERVER (telegram-server)
# setup script to install dependencies and configure environment


stringContains () { [ -z "${2##*$1*}" ]; }

check_libreadline () {
	# fix for a very specific type of error
	ls /usr/local/opt/readline/lib/libreadline.6.dylib
	if [ "$?" == "1" ]; then		readline
		rm -rf /usr/local/opt/
		ln -s ${READLINE_BASE_DIR} /usr/local/opt/readline
	fi
}

if [ "$1" != "skip-cli" ]; then 

########### PHASE 1: MAKING THE CLI FOR THE AI TO SEND/RECEIVE MSGS ##########
git clone --recursive https://github.com/vysheng/tg.git
cd tg

sudo apt-get install libreadline-dev libconfig-dev libssl-dev lua5.2 liblua5.2-dev libevent-dev libjansson-dev libpython-dev
if [ "$?" != "0" ] && stringContains "Darwin" `uname -s` ; then
	# pretty safe to say that we're on an OSX, so do all the OSX thingy
	# if we're not then too bad, but no harm
	brew install libconfig readline lua libevent jansson libgcrypt

	READLINE_VERSION=`ls /usr/local/Cellar/readline`
	READLINE_VERSION=(${READLINE_VERSION// / })
	READLINE_VERSION=${READLINE_VERSION[@]:(-1)}
	READLINE_BASE_DIR=/usr/local/Cellar/readline/${READLINE_VERSION}

	export CFLAGS="-I/usr/local/include -I${READLINE_BASE_DIR}/include"
	export LDFLAGS="-L/usr/local/lib -L${READLINE_BASE_DIR}/lib"
else
	echo "Not on mac/darwin but no apt-get"
fi

./configure
sed -i '' 's/ -Werror / /' Makefile
make

###############################################################################

else
	echo "Skipping telegram-cli installation..."
fi


if [ "$1" != "skip-python" ]; then 

########### PHASE 2: MAKING THE CLI FOR THE AI TO SEND/RECEIVE MSGS ##########

# check if we have python3 installed first
REQUIRED_PYTHON3_VERSION=3.6
PYTHON3_VERSION=`python3 --version`
if [ "$?" == "127" ] || ! stringContains "${REQUIRED_PYTHON3_VERSION}" "${PYTHON3_VERSION}" ; then
	# no py3
	echo "Could not locate Python ${REQUIRED_PYTHON3_VERSION}"
	echo "Python >= ${REQUIRED_PYTHON3_VERSION} has to be installed to proceed. Install Python ${REQUIRED_PYTHON3_VERSION} on this machine? (y/n):"
	read INSTALL_PYTHON
	if [ "${INSTALL_PYTHON}" == "yes" ]; then
		# install py3 - currently only linux or OSX path...
		sudo apt-get install python${REQUIRED_PYTHON3_VERSION}
		if [ "$?" == "127" ]; then
			brew install python3
		fi
	else
		echo 'Aborting setup'
		exit 1
	fi
fi

echo 'Initializing setup...'
echo 'Please input Telegram api_id: '
read -s TG_API_ID 
echo 'Please input Telegram api_hash: '
read -s TG_API_HASH
echo 'Generating folders'
mkdir creds
mkdir sessions
echo 'Generating credentials file'
echo "{\"api_id\": ${TG_API_ID}, \"api_hash\": \"${TG_API_HASH}\"}" >> creds/telegram.json
python3 -m venv virtualenv
source virtualenv/bin/activate
pip install -r requirements.txt

###############################################################################

else
	echo "Skipping python requirements installation..."
fi

