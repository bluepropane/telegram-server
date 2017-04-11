from pytg import Telegram
from pytg.utils import coroutine

"""
Example message schema
{
  "own": false,
  "text": "Lololol",
  "peer": {
    "username": "liweiong",
    "last_name": "Ong",
    "phone": "16506860567",
    "id": "$010000001bbe580e7f52fe2c69cb9f77",
    "first_name": "Liwei",
    "name": "Liwei",
    "cmd": "$010000001bbe580e7f52fe2c69cb9f77",
    "when": "2017-04-11 02:49:46",
    "flags": 524289,
    "peer_id": 240696859,
    "type": "user"
  },
  "date": 1491903927,
  "event": "message",
  "sender": {
    "username": "liweiong",
    "last_name": "Ong",
    "phone": "16506860567",
    "id": "$010000001bbe580e7f52fe2c69cb9f77",
    "first_name": "Liwei",
    "name": "Liwei",
    "cmd": "$010000001bbe580e7f52fe2c69cb9f77",
    "when": "2017-04-11 02:49:46",
    "flags": 524289,
    "peer_id": 240696859,
    "type": "user"
  },
  "service": false,
  "id": "010000001bbe580ede930000000000007f52fe2c69cb9f77",
  "flags": 256,
  "receiver": {
    "username": "liweiong",
    "last_name": "Ong",
    "phone": "16506860567",
    "id": "$010000001bbe580e7f52fe2c69cb9f77",
    "first_name": "Liwei",
    "name": "Liwei",
    "cmd": "$010000001bbe580e7f52fe2c69cb9f77",
    "when": "2017-04-11 02:49:46",
    "flags": 524289,
    "peer_id": 240696859,
    "type": "user"
  },
  "unread": false
}
"""

class TelegramController(object):

	def __init__(self, port=3007):
		self.port = port
		self.receiver = None
		self.sender = None
		self.observers = []
		self._run_tg_server()
		# self._start_receiver()

	def _run_tg_server(self):
		tg = Telegram(
			telegram="../../tg/bin/telegram-cli",
			pubkey_file="../../tg/tg-server.pub",
			port=self.port)
		self.receiver = tg.receiver
		self.sender = tg.sender

	@coroutine
	def _receive_message_callback(self):
		try:
			while True:
				msg = (yield) # it waits until it got a message, stored now in msg.
				if hasattr(msg, 'text'):
					print msg.text
				self._notify_observers(msg)

		except KeyboardInterrupt:
			self.receiver.stop()

	def _start_receiver(self):
		self.receiver.start()
		print 'Telegram receiver started on port %s, waiting for messages...' % self.port
		self.receiver.message(self._receive_message_callback())
		self.receiver.stop()

	def _notify_observers(self, msg):
		for observer in self.observers:
			observer(msg)

	def on_message(self, callback):
		self.observers.append(callback)

	def send(self, usernames, msg):
		if isinstance(usernames, str):
			usernames = [usernames]

		if isinstance(usernames, list):
			for username in usernames:
				self.sender.send_msg(username, msg.decode('utf-8'))

if __name__ == '__main__':
	TelegramController()