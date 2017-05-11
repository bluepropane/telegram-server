"""
Telegram adapter for the AI account. Singleton instance. 
"""
from pytg import Telegram
from pytg.utils import coroutine
from queue import Queue
from conversation_util import Conversation
import threading
import db
import logging

LOGGER = logging.getLogger(__name__)


class TelegramAI(object):

    instance = None
    
    def __init__(self):
        self.sender = None
        self.receiver = None
        self.observers = []
        self.phone = None
        self.queue = Queue()
        self._init_telegram()
        self._load_ai_info()
        self.start_receiver()
        self.start_ai()

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
                LOGGER.info("event: {}".format(msg))
                if msg.event == 'message':
                    self._log_chat_history_db(msg)
                    if not msg.own:
                        # we're only interested in text messages (for now)
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

    def send(self, peers, msg):
        """
        Sends a message to the specified username(s)
        """
        if isinstance(peers, str):
            peers = [peers]

        if isinstance(peers, list):
            for peer in peers:
                self.sender.send_msg(peer, msg)

    def _start_ai(self):
        """
        This is a blocking method; should be run on a separate thread.
        """
        LOGGER.info('Started telegram sender; waiting for messages from receiver...')
        try:
            while True:
                msg = self.queue.get()
                LOGGER.info('Picked up message from queue - {}'.format(msg))
                self._process_response(msg)
                self.queue.task_done()
        except Exception as err:
            LOGGER.error('Sender worker error: %r' % err)
            LOGGER.info('Restarting telegram sender...')
            self._start_ai()
            raise Exception(err)

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

    def add_contact(self, phone, first_name, last_name=''):
        """
        Adds a contact. Contact must be added before the ai can start a conversation.
        """
        result = self.sender.contact_add(phone, first_name, last_name)
        if not result:
            LOGGER.error('Telegram phone {} could not be added'.format(phone))
            raise Exception('TELEGRAM_PHONE_NOT_FOUND')

        peer_id = result[0].id
        return peer_id

    def _process_response(self, msg):
        """process message"""
        reply_message = Conversation(msg).process_response()
        if reply_message is not False:
            self.send('{}'.format(msg.sender.id), reply_message)

    @staticmethod
    def _log_chat_history_db(msg):
        """
        Insert message into db for recording
        """
        if msg.text:
            msg_type = 'SENT' if msg.own else 'RECEIVED'
            recipient_phone = msg.receiver.phone if msg.own else msg.sender.phone

            sql = ("""
                INSERT INTO chat_history (`message_type`, `recipient_id`, `text`, `event_id`)
                VALUES (
                    %s,
                    (SELECT r.id FROM recipient r WHERE r.phone = %s LIMIT 1),
                    %s,
                    (SELECT r.event_id FROM recipient r WHERE r.phone = %s LIMIT 1)
                )
            """)

            db.write(sql, params=(msg_type, recipient_phone, msg.text, recipient_phone))


def get_instance():
    if TelegramAI.instance is None:
        TelegramAI.instance = TelegramAI()

    return TelegramAI.instance


if __name__ == '__main__':
    a = get_instance()
    while True:
        input()
