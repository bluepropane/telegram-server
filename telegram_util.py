"""
Telegram adapter for the AI account. Singleton instance. 
"""
from pytg import Telegram
from pytg.utils import coroutine
from queue import Queue
import threading
import db
import logging

LOGGER = logging.getLogger(__name__)


class TelegramAI(object):

    instance = None
    
    def __init__(self):
        self.sender = None
        self.receiver = None
        self.observer = None
        self.phone = None
        self.queue = Queue()
        self._init_telegram()
        self._load_ai_info()

    def _init_telegram(self):
        """
        Init telegram adapter with the AI's credentials for conversations.
        """
        LOGGER.info('Connecting to Telegram servers...')
        self.tg = Telegram(
            telegram="tg/bin/telegram-cli",
            pubkey_file="tg/tg-server.pub",
            port=4460)
        self.receiver = self.tg.receiver
        self.sender = self.tg.sender
        self.sender.default_answer_timeout = 5.0

    def _load_ai_info(self):
        LOGGER.info('Loading bot info...')
        info = self.sender.whoami()
        for k, v in info.items():
            LOGGER.info('-- {}: {}'.format(k, v))
        if 'error' not in info:
            self.phone = info['phone']

    def _start_receiver(self):
        """
        This is a blocking method; should be run on a separate thread.
        """
        self.receiver.start()
        LOGGER.info('Started telegram receiver server')
        self.receiver.message(self._receiver_main_loop())

    @coroutine
    def _receiver_main_loop(self):
        """
        main message callback handler
        """
        try:
            while True:
                msg = (yield) # waits until it receives a message
                if msg.event == 'message' and not msg.own:
                    # we're only interested in text messages (for now)
                    LOGGER.info("Message: ", msg)
                    self.queue.put(msg)

        except Exception as err:
            LOGGER.error('Err: %r \n\n'.format(err))
        finally:
            LOGGER.info('Shutting down receiver')
            self.receiver.stop()
            TelegramAI.instance = None

    def start_receiver(self):
        """
        Starts the receiver on a separate thread
        """
        receiver_worker = threading.Thread(
            target=self._start_receiver,
            args=(),
            name='telegram-receiver-thread'
        )
        receiver_worker.setDaemon(True)
        receiver_worker.start()

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
                self.sender.send_msg(username, msg)

    def _start_ai(self):
        """
        This is a blocking method; should be run on a separate thread.
        """
        LOGGER.info('Started telegram sender; waiting for messages from receiver...')
        try:
            while True:
                msg = self.queue.get()
                LOGGER.info('Picked up message from queue - {}: {}'.format(msg.sender.name, msg.text))
                self.process_response(msg)
                self.queue.task_done()
        except Exception as err:
            LOGGER.error('Sender worker error: %r' % err)
            LOGGER.info('Restarting telegram sender...')
            self._start_ai()

    def start_ai(self):
        """
        Sender is acting as a worker; processes message from receiver through the queue.
        """
        sender_worker = threading.Thread(
            target=self._start_ai,
            args=(),
            name='telegram-sender-worker'
        )
        sender_worker.setDaemon(True)
        sender_worker.start()

    def process_response(self, msg):
        """
        AI conversation logic goes here.
        @param msg: Message object. sender details are stored
                    in msg.sender, while receiver details (the bot) are stored in msg.receiver.
                    Message text content (from the sender) is stored in msg.text
                    See below for an example.
        """
        # db.insert_one('chat_history', {
            
        # })
        if msg.text.lower() == 'hi':
            response_message = 'Hi there {.first_name}!'.format(msg.sender)
        else:
            response_message = 'Sorry, I didn\'t quite get you.'

        self.send('@{}'.format(msg.sender.username), response_message)


def get_instance():
    if TelegramAI.instance is None:
        TelegramAI.instance = TelegramAI()

    return TelegramAI.instance


if __name__ == '__main__':
    a = get_instance()
    a.start_receiver()
    a.start_ai()
    while True:
        input()
