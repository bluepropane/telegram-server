"""
Telegram adapter instance for the AI account. Should be a singleton. 
"""
from pytg import Telegram
from pytg.utils import coroutine
from queue import Queue
import threading
import db


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
        print('Connecting to Telegram servers...')
        self.tg = Telegram(
            telegram="tg/bin/telegram-cli",
            pubkey_file="tg/tg-server.pub",
            port=4460)
        self.receiver = self.tg.receiver
        self.sender = self.tg.sender
        self.sender.default_answer_timeout = 5.0

    def _load_ai_info(self):
        print('Loading bot info...')
        info = self.sender.whoami()
        for k, v in info.items():
            print('-- {}: {}'.format(k, v))
        if 'error' not in info:
            self.phone = info['phone']

    def _start_receiver(self):
        """
        This is a blocking method; should be run on a separate thread.
        """
        self.receiver.start()
        print('Started telegram receiver server')
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
                    print("Message: ", msg)
                    self.queue.put(msg)

        except Exception as err:
            print('Err: %r \n\n'.format(err))
        finally:
            print('Shutting down receiver')
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
        print('Started telegram sender; waiting for messages from receiver...')
        try:
            while True:
                msg = self.queue.get()
                print('Picked up message from queue - {}: {}'.format(msg.sender.name, msg.text))
                self.process_response(msg)
                self.queue.task_done()
        except Exception as err:
            print('Sender worker error: %r'.format(err))
            print('Restarting telegram sender...')
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
        """
        # db.insert_one('chat_history', {
            
        # })
        self.send('@{}'.format(msg.sender.username), 'Hi there {}!'.format(msg.sender.first_name))


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
