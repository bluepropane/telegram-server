"""
Telegram adapter instance for the AI account. Should be a singleton. 
"""
from pytg import Telegram as tg
from pytg.utils import coroutine
import json
import os



class Telegram(object):

    instance = None
    
    def __init__(self):
        self.sender = None
        self.receiver = None
        self.observer = None
        self._init_telegram()

    def _init_telegram(self):
        """
        Init telegram adapter with the AI's credentials for conversations.
        """
        print('Connecting to Telegram servers...')
        self.tg = tg(
            telegram="tg/bin/telegram-cli",
            pubkey_file="tg/tg-server.pub")
        self.receiver = self.tg.receiver
        self.sender = self.tg.sender

    def on_message(self, callback):
        """
        add an observer for message event
        @param callback: called on message event with arguments (update_object). update_object can be
                         of type {telethon.tl.types.UpdateShortChatMessage} or
                                 {telethon.tl.types.UpdateShortMessage}
        """
        self.observer.append(callback)

    def send(self, usernames, msg):
        if isinstance(usernames, str):
            usernames = [usernames]

        if isinstance(usernames, list):
            for username in usernames:
                self.send_message(username, msg)

def get_instance():
    if Telegram.instance is None:
        Telegram.instance = Telegram()

    return Telegram.instance
