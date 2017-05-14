import telegram_util
import logging
from phone_util import sanitize_phone_number
from broadcast_models import Broadcast

LOGGER = logging.getLogger(__name__)


class BroadcastController(object):

    def post(self, request_params, response):
        LOGGER.info('calling broadcast service with request_params {}'.format(request_params))
        broadcast = Broadcast(request_params.get('recipients')['0'])
        broadcast.send(request_params.get('message'))

        return {}