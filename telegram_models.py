from telethon import TelegramClient, RPCError
from telethon.tl.functions.contacts.get_contacts import GetContactsRequest
import json
import os
import logging

LOGGER = logging.getLogger(__name__)
config = json.load(open('creds/telegram.json'))


class TelegramUserAccount(TelegramClient):

    def __init__(self, session_user_id, user_phone=None, proxy=None):

        api_id = config.get('api_id')
        api_hash = config.get('api_hash')
        super().__init__(os.path.join('sessions', session_user_id), api_id, api_hash)
        self.api_id = api_id
        self.api_hash = api_hash
        self.user_phone = user_phone
        self.result = {}
        if user_phone is None:
            self.user_phone = session_user_id 
        if self.user_phone[0] != '+':
            self.user_phone = '+' + self.user_phone


        # Store all the found media in memory here,
        # so it can be downloaded if the user wants
        # self.found_media = set()

    def __enter__(self):
        """Initialize connection with Telegram server"""
        LOGGER.info('Connecting to Telegram servers...')
        self.connect()
        LOGGER.info(self.is_user_authorized())
        return self


    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up after use"""
        LOGGER.info('Telegram account session closed with exc_type={}, exc_val={}, exc_tb={}'\
            .format(exc_type, exc_val, exc_tb))
        self.disconnect()

    def authorize(self):
        """
        ensure we're authorized and have access
        """
        if not self.is_user_authorized():
            LOGGER.info('First run. Sending code request...')
            self.send_code_request(self.user_phone)
            return False
        else:
            LOGGER.info('User is already authorized. Proceeding...')
            return True

    def authorize_code(self, code):
        try:
            signed_in = self.sign_in(self.user_phone[1:], code)
            if not signed_in:
                raise Exception('Sign in failed, please try again.')
        # Two-step verification may be enabled
        except RPCError as e:
            if e.password_required:
                pw = getpass(
                    'Two step verification is enabled. Please enter your password: ')
                elf.sign_in(password=pw)
            else:
                raise e

    def get_contacts(self):
        result = self.invoke(GetContactsRequest(self.api_hash))
        self.contacts = []
        for user in result.users:
            self.contacts.append({
                'first_name': user.first_name,    
                'last_name': user.last_name,    
                'phone': user.phone,    
                'id': user.id
            })
