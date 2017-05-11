from telethon import TelegramClient, RPCError
from telethon.tl.functions.contacts.get_contacts import GetContactsRequest
from db import redis
import json
import math
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
        self.contacts = []
        self.page = 0
        self.limit = None
        self.last_page = True
        self.session_user_id = session_user_id
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

    def _parse_selected_contacts_range(self):
        if self.limit:
            start_index = self.limit * self.page
            end_index = start_index + self.limit
        else:
            return

        return start_index, end_index

    def get_contacts(self, limit=None, page=None):
        if limit:
            self.limit = int(limit)
            self.page = int(page) if page else self.page


        result = redis.lrange(self.user_phone, 0, -1)
        if not result:
            response = self.invoke(GetContactsRequest(self.api_hash))
            result = response.users

            for user in result:
                self.contacts.append({
                    'first_name': user.first_name,    
                    'last_name': user.last_name,    
                    'phone': user.phone,    
                    'id': user.id
                })
            LOGGER.info('contacts: {}'.format(self.contacts));
            self.contacts.sort(key=lambda k: k['first_name'])
            serialized_contacts = [json.dumps(user) for user in self.contacts]
            redis.rpush(self.session_user_id, *serialized_contacts)
        else:
            LOGGER.info('Using cached contacts result from redis')
            start_index, end_index = self._parse_selected_contacts_range()

            LOGGER.info('lolsult {}'.format(result[start_index:end_index]))
            self.contacts = [json.loads(user.decode()) for user in result[start_index:end_index]]

        if self.limit is None:
            self.last_page = 0
        else:
            self.last_page = math.ceil(len(result) / self.limit)

        redis.expire(self.session_user_id, 900)
