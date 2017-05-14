import logging
import db
import telegram_util

LOGGER = logging.getLogger(__name__)


class Broadcast(object):

    def __init__(self, recipients):
        super().__init__()
        self.recipients = None
        self.ai = telegram_util.get_instance()
        self._load_recipients_from_recipient_ids(recipients)

    def _load_recipients_from_recipient_ids(self, recipients):
        sql = ("""
            SELECT r.peer_id FROM recipient r
            WHERE r.id IN %s
        """)

        params = [recipient['id'] for recipient in recipients]

        self.recipients = db.read(sql, params=(params,))
        LOGGER.info('loaded recipients: {}'.format(self.recipients))

    def send(self, message):
        for recipient in self.recipients:
            self.ai.send(recipient['peer_id'], message)