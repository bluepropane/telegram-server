"""
Telegram adapter instance for the AI account. Should be a singleton. 
"""
from pytg import Telegram as tg
from pytg.utils import coroutine
from queue import Queue
import threading


class TelegramAI(object):

    instance = None
    
    def __init__(self):
        self.sender = None
        self.receiver = None
        self.observer = None
        self.queue = Queue()
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

    def _start_receiver(self):
        """
        This is a blocking method; should be run on a separate thread.
        """
        self.receiver.start()
        self.receiver.message(self.receiver_main_loop())

    @coroutine
    def receiver_main_loop(self):
        """
        main message callback handler
        """
        try:
            while True:
                msg = (yield) # it waits until it got a message, stored now in msg
                print("Message: ", msg)
                # do more stuff here!

        except Exception as err:
            print('Err: %r \n\nShutting down receiver'.format(err))
            self.receiver.close()
        finally:
            print('Shutting down receiver')
            self.receiver.close()

    def start_receiver(self):
        """
        Starts the receiver on a separate thread
        """
        receiver_worker = threading.Thread(
            target=self._start_receiver,
            args=(),
            name='telegram-receiver-process'
        )
        receiver_worker.setDaemon(True)
        receiver_worker.start()
        print('Started telegram receiver server')

    def on_message(self, callback):
        """
        add an observer for message event
        @param callback: called on message event with arguments (update_object). update_object can be
                         of type {telethon.tl.types.UpdateShortChatMessage} or
                                 {telethon.tl.types.UpdateShortMessage}
        """
        self.observer.append(callback)

    def send(self, usernames, msg):
        """
        Sends a message to the specified username(s)
        """
        if isinstance(usernames, str):
            usernames = [usernames]

        if isinstance(usernames, list):
            for username in usernames:
                self.send_msg(username, msg)


def get_instance():
    if TelegramAI.instance is None:
        TelegramAI.instance = TelegramAI()

    return TelegramAI.instance
