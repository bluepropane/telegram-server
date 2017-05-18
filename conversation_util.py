import db


class Conversation(object):

    def __init__(self, msg):
        super().__init__()
        self.recipient_phone = msg.sender.phone
        self.recipient_id = None
        self.msg = msg
        self.response = None

    def _load_context_info(self):

        sql = ("""
            SELECT r.chat_status, e.event_id FROM recipient AS r
            JOIN event AS e
                ON e.id = r.event_id
            WHERE r.phone = %s
        """)

        row = db.read(sql, params=(self.recipient_phone,))
        if row:
            self.recipient_chat_status = row['chat_status']

    def _update_chat_status(self, chat_status):

        sql = ("""
            UPDATE `recipient` SET chat_status = 10
            WHERE id = %s
        """)

        db.write(sql, params=(self.recipient_id,))

    def _handle_initial_rsvp(self):
        """
        First user response (attending RSVP) after initial invitations have been sent out.
        """
        if self.msg.text.lower() == 'yes':
            self.response = 'Awesome! May I know the date which would best suit you to attend the event?'
        elif self.msg.text.lower() == 'no':
            self.response = ["""That's such a pity. Don't worry, I'll let {event_organiser} know!"""]

    def process_response(self):
        """
        AI conversation logic goes here.
        @param msg: Message object. sender details are stored
                    in msg.sender, while receiver details (the bot) are stored in msg.receiver.
                    Message text content (from the sender) is stored in msg.text
                    See below for an example.
        """
        if self.chat_status == 10:
            self._update_chat_status(20)
            self._handle_initial_rsvp()

        if self.msg.text.lower() == 'hi':
            self.response = 'Hi there {.first_name}!'.format(self.msg.sender)
        elif self.msg.text.lower() == 'u suck':
            self.response = 'u suck more suck my dik fag {.first_name}!'.format(self.msg.sender)
        else:
            self.response = False


        return self.response
