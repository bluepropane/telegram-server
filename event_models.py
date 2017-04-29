import logging
import db

LOGGER = logging.getLogger(__name__)


class Event(object):

    def __init__(self, event_id):
        super().__init__()
        self.event_id = event_id

    def _load_recipients_list_from_db(self):
    	"""
    	Load the recipients associated with the event id from db
    	"""
    	sql = ("""
    		SELECT r.name, r.phone FROM recipient r
    		WHERE r.event_id = %s
    	""")

    	result = db.read(sql, params=(self.event_id,))

    def start_conversations(self):
    	"""
    	Get the telegram AI to start the event-related conversations with the recipients
    	"""
    	self._load_recipients_list_from_db()