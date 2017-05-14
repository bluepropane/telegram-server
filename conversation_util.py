import db


class Conversation(object):

    def __init__(self, msg):
        super().__init__()
        self.recipient_phone = msg.sender.phone
        self.msg = msg
        self.response = None

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
        if self.msg.text.lower() == 'hi':
            self.response = 'Hi there {.first_name}!'.format(self.msg.sender)
        elif self.msg.text.lower() == 'u suck':
            self.response = 'u suck more suck my dik fag {.first_name}!'.format(self.msg.sender)
        else:
            self.response = False

        return self.response
        
        else:
            self.response = False