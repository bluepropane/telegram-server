if [ "$1" == "_run" ]; then
	. virtualenv/bin/activate
	python server.py
else
	nohup ./start_server.sh _run >/dev/null 2>log/main-process.log &
fi
