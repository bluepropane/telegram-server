import logging
import db
import telegram_util

LOGGER = logging.getLogger(__name__)


class Event(object):

    def __init__(self, event_id):
        super().__init__()
        self.event_id = event_id
        self.event_name = None
        self.event_organiser = None
        self.ai = telegram_util.get_instance()

    def _load_recipients_list_from_db(self):
        """
        Load the recipients associated with the event id from db
        """
        sql = ("""
            SELECT r.id, r.name, r.phone, r.peer_id FROM recipient r
            WHERE r.event_id = %s
            -- AND r.chat_status = 0
            -- AND r.recipient_status = 'ACTIVE'
        """)

        self.recipients = db.read(sql, params=(self.event_id,))
        LOGGER.info('Loaded recipients from db: {}'.format(self.recipients))

    def _load_event_details(self):
        """
        Load event details
        """

        sql = ("""
            SELECT e.event_name, e.event_organiser FROM event e
            WHERE e.id = %s
            LIMIT 1
        """)

        row = db.read(sql, params=(self.event_id,))
        if not row:
            LOGGER.error('Event with id {} not found'.format(self.event_id))
            raise Exception('EVENT_NOT_FOUND')

        LOGGER.info('Loaded event details from db: {}'.format(row))
        self.event_name = row['event_name']
        self.event_organiser = row['event_organiser']


    def _update_peer_id(self, recipient):
        """
        Update peer_id of specified recipient in the db.
        """
        sql = ("""
            UPDATE `recipient` SET peer_id = %s
            WHERE id = %s
        """)
        print(recipient['id'], recipient['peer_id'])
        db.write(sql, params=(recipient['peer_id'], recipient['id']))

    def _start_conversation(self, recipient):
        """
        Starts the event-related conversation with the specified recipient
        """
        message = """
Hey {name}! 

This is Hey.ai and I am collecting event responses on behalf of your friend {organiser_name}. \
Will you be interested in going for {event_name}?
        """.format(**{
            'name': recipient.get('name'),
            'organiser_name': self.event_organiser,
            'event_name': self.event_name
        })

        self.ai.send(recipient.get('peer_id'), message)

        sql = ("""
            UPDATE `recipient` SET chat_status = 1
            WHERE id = %s
        """)

        db.write(sql, params=(recipient['id'],))

        db.insert_one('chat_history', {
            'text': message,
            'message_type': 'SENT'
        })

    def start_conversations(self):
        """
        Get the telegram AI to start the event-related conversations with the recipients
        """
        self._load_event_details()
        self._load_recipients_list_from_db()

        if not self.recipients:
            LOGGER.warn('No recipients found for event id {}'.format(self.event_id))

        for recipient in self.recipients:
            peer_id = self.ai.add_contact(recipient.get('phone'), recipient.get('name'))
            recipient['peer_id'] = peer_id
            self._update_peer_id(recipient)
            self._start_conversation(recipient)
