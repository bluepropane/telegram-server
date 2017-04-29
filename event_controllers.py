import telegram_util
import logging
from phone_util import sanitize_phone_number
from event_models import Event

LOGGER = logging.getLogger(__name__)


class EventController(object):

    def get(self, request_params, response):
        """
        Get the bot chat history with all recipients for a particular event
        """
        phone_number = sanitize_phone_number(request_params.get('phone')[0])

    def post(self, request_params, response):
        """
        This endpoint is called for initiating the telegram bot message flow.
        @param request_params: should contain 'recipients', an array of name and phone numbers
        """
        phone_number = sanitize_phone_number(request_params.get('phone')[0])
        event = Event(request_params.get('id'))
        event.start_conversations()

        return result