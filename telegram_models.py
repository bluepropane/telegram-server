from telethon import TelegramClient, RPCError
import json
import os


config = json.load(open('creds/telegram.json'))


class TelegramUserAccount(TelegramClient):

    def __init__(self, session_user_id, user_phone=None, proxy=None):

        super().__init__(os.path.join('sessions', session_user_id), config.get('api_id'),
                            config.get('api_hash'))
        self.user_phone = user_phone

        # Store all the found media in memory here,
        # so it can be downloaded if the user wants
        # self.found_media = set()

        print('Connecting to Telegram servers...')
        self.connect()
        self.authorize()

    def authorize(self):
        """
        ensure we're authorized and have access
        """
        if not self.is_user_authorized():
            print('First run. Sending code request...')
            self.send_code_request(self.user_phone)
            return False
        else:
            print('User is already authorized. Proceeding...')
            return True

    def authorize_code(self, code):
        try:
            self.sign_in(user_phone, code)

        # Two-step verification may be enabled
        except RPCError as e:
            if e.password_required:
                pw = getpass(
                    'Two step verification is enabled. Please enter your password: ')
                code_ok = self.sign_in(password=pw)
            else:
                raise e
