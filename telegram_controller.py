from telethon import TelegramClient


class TelegramController(TelegramClient):

	def __init__(self, port=3007):
		self.port = port
		self.receiver = None
		self.sender = None
		self.observers = []
		self._run_tg_server()
		# self._start_receiver()

	def _run_tg_server(self):
		self.tg = Telegram(
			telegram="tg/bin/telegram-cli",
			pubkey_file="tg/tg-server.pub",
			port=self.port)
		self.receiver = self.tg.receiver
		self.sender = self.tg.sender

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
    finally:
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