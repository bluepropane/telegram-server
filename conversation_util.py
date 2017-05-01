import db


class Conversation(object):

    def __init__(self, msg):
        super().__init__()
        self.recipient_phone = msg.sender.phone

    def _load_context_info(self):

        sql = ("""
            SELECT r.chat_status, e.event_id FROM recipient AS r
            JOIN event AS e
                ON e.id = r.event_id
            WHERE r.phone = %s
        """)

        db.read(sql, params=(self.recipient_phone,))

    def process_response(self):
        """
        AI conversation logic goes here.
        @param msg: Message object. sender details are stored
                    in msg.sender, while receiver details (the bot) are stored in msg.receiver.
                    Message text content (from the sender) is stored in msg.text
                    See below for an example.
        """
        if msg.text.lower() == 'hi':
            response_message = 'Hi there {.first_name}!'.format(msg.sender)
        else:
            response_message = 'Sorry, I didn\'t quite get you.'

        self.send('@{}'.format(msg.sender.username), response_message)

    def _log_chat_history_db(self):
        """
        Insert message into db for recording
        """
        sql = ("""
            INSERT INTO chat_history (`text`, )
        """)
        db.insert_one('chat_history', {
            'text': msg.sender.text
        })