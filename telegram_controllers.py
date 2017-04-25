from telegram_models import TelegramUserAccount
import telegram_util
import re


class TelegramController(object):

    def get(self, request_params, response):
        """
        Endpoint called for retrieving the telegram contacts of the specified phone number. The phone number has
        to be logged in first for this endpoint to work.
        """
        phone_number = self._sanitize_phone_number(request_params.get('phone')[0])
        telegram_user = TelegramUserAccount(phone_number, user_phone=phone_number)
        if not telegram_user.is_user_authorized():
            print('Telegram user unauthorized.')
            raise Exception('Telegram user unauthorized.')
        else:
            print('Telegram user authorized, fetching contacts...')
            telegram_user.get_contacts()

        return {'contacts': telegram_user.contacts}

    def post(self, request_params, response):
        """
        This endpoint is called for initiating the authorization flow.
        @param request_params: should contain an 'type' paramter. 'onboard' is for
                the initialization of the flow, while 'code' is for verifying the authorization code.
        """
        phone_number = self._sanitize_phone_number(request_params.get('phone')[0])
        auth_type = request_params.get('type')[0]
        telegram_user = TelegramUserAccount(phone_number, user_phone=phone_number)
        result = {}
        if not telegram_user.is_user_authorized():
            if auth_type == 'onboard':
                print('Sending telegram verification code to {}'.format('+' + phone_number))
                telegram_user.send_code_request(phone_number)
                result = {"identifier": telegram_user.phone_code_hashes['+' + phone_number]}
            elif auth_type == 'code':
                telegram_user.phone_code_hashes['+' + phone_number] = request_params.get('identifier')
                telegram_user.authorize_code(request_params.get('code'))
        else:
            response.status = 208

        return result

    @staticmethod
    def _sanitize_phone_number(number):
        """
        Take away the leading '+' for standardization. Just add it back if needed.
        @param number: phone number
        """
        if isinstance(number, int):
            number = str(number)
        elif not isinstance(number, str):
            raise Exception('Invalid phone number: not a str')
        if number[0] == '+':
            number = number[1:]
        if re.match(r'^[0-9]+$', number) is None:
            raise Exception('Invalid phone number: must be 0-9')

        return number
