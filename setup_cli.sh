#!/bin/bash

# TELEGRAM SERVER (telegram-server)
# setup script to install dependencies and configure environment


git clone --recursive https://github.com/vysheng/tg.git && cd tg

# READLINE_BASE_DIR=/usr/local/opt/readline
brew install libconfig readline lua libevent jansson

READLINE_VERSION=`ls /usr/local/Cellar/readline`
READLINE_VERSION=(${READLINE_VERSION// / })
READLINE_VERSION=${READLINE_VERSION[0]}
READLINE_BASE_DIR=/usr/local/Cellar/readline/${READLINE_VERSION}

export CFLAGS="-I/usr/local/include -I${READLINE_BASE_DIR}/include"
export LDFLAGS="-L/usr/local/lib -L${READLINE_BASE_DIR}/lib -L/usr/local/opt/openssl/lib"
export CPPFLAGS="-I/usr/local/opt/openssl/include"

check_libreadline () {
	# fix for a very specific type of error
	ls /usr/local/opt/readline/lib/libreadline.6.dylib
	if [ "$?" == "1" ]; then		
		rm -rf /usr/local/opt/readline
		ln -s ${READLINE_BASE_DIR} /usr/local/opt/readline
	fi
}

./configure
make