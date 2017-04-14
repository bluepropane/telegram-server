from telethon import TelegramClient, RPCError
import json

config = json.load(open('creds/telegram.json'))


class TelegramController(TelegramClient):

    def __init__(self, session_user_id, user_phone, proxy=None):

        print('Initializing interactive example...')
        super().__init__(session_user_id, config.get('api_id'), config.get('api_hash'), proxy)

        # Store all the found media in memory here,
        # so it can be downloaded if the user wants
        self.found_media = set()

        print('Connecting to Telegram servers...')
        self.connect()

    def authorize(self):

    def authorize_code(self, code):
        try:
            code_ok = self.sign_in(user_phone, code)

        # Two-step verification may be enabled
        except RPCError as e:
            if e.password_required:
                pw = getpass(
                    'Two step verification is enabled. Please enter your password: ')
                code_ok = self.sign_in(password=pw)
            else:
                raise e

	def on_message(self, callback):
		"""
		add an observer for message event
		@param callback: called on message event with arguments (update_object). update_object can be
						 of type {telethon.tl.types.UpdateShortChatMessage} or
						 		 {telethon.tl.types.UpdateShortMessage}
		"""
		self.add_update_handler(callback)

	def send(self, usernames, msg):
		if isinstance(usernames, str):
			usernames = [usernames]

		if isinstance(usernames, list):
			for username in usernames:
				self.sender.send_msg(username, msg.decode('utf-8'))

if __name__ == '__main__':
	TelegramController()