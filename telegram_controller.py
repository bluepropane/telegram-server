from telethon import TelegramClient, RPCError
import json
import pytg

config = json.load(open('creds/telegram.json'))


class TelegramController(TelegramClient):

    def __init__(self, session_user_id, user_phone=None, proxy=None):

        print('Initializing interactive example...')
        super().__init__(session_user_id, config.get('api_id'), config.get('api_hash'))
        self.user_phone = user_phone

        # Store all the found media in memory here,
        # so it can be downloaded if the user wants
        self.found_media = set()

        print('Connecting to Telegram servers...')
        self.connect()
        self.authorize()

    def authorize(self):
        """
        ensure we're authorized and have access
        """
        if not self.is_user_authorized():
            print('First run. Sending code request...')
            self.send_code_request(user_phone)
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
                self.send_message(username, msg)

if __name__ == '__main__':
    a =TelegramController('16506860567')

    def on_message(msg_object):
        print('receivd message! {}'.format(msg_object))
        if hasattr(msg_object, 'user_id') and hasattr(msg_object, 'message'):
            print("{}: {}".format(msg_object.user_id, msg_object.message))

    # a.on_message(on_message)
    # a.send('@liweiong', 'hi')