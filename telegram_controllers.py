from telegram_models import TelegramUserAccount
import telegram_util


class TelegramController(object):

    def get(self, request_params):
        phone_number = self._sanitize_phone_number(request_params.get('phone'))
        telegram_user = TelegramUserAccount(phone_number, user_phone=phone_number)
        if not telegram_user.is_user_authorized():
            raise Exception('Telegram user unauthorized.')
        else:
            telegram_user.get_contacts()

    def post(self, request_params):
        """
        This endpoint is called for initiating the authorization flow.
        @param request_params: should contain an 'type' paramter. 'onboard' is for
                the initialization of the flow, while 'code' is for verifying the authorization code.
        """
        phone_number = self._sanitize_phone_number(request_params.get('phone'))
        auth_type = request_params.get('type')
        telegram_user = TelegramUserAccount(phone_number, user_phone=phone_number)
        if not telegram_user.is_user_authorized():
            if auth_type == 'onboard':
                telegram_user.send_code_request(phone_number)
            elif auth_type == 'code':
                telegram_user.authorize_code(phone_number)

        return {}

    @staticmethod
    def _sanitize_phone_number(self, number):
        """
        Take away the leading '+' for standardization. Just add it back if needed.
        @param number: phone number
        """
        if isinstance(number, int):
            number = str(number)
        elif not isinstance(number, str):
            raise Exception('Invalid phone number')
        if number[0] == '+':
            number = number[1:]
        if re.match(r'^[0-9]+$', number) is None:
            raise Exception('Invalid phone number')

        return number


if __name__ == '__main__':
    a =TelegramController('16506860567')
    print('yo', a.receiver)

    def on_message(msg_object):
        print('receivd message! {}'.format(msg_object))
        if hasattr(msg_object, 'user_id') and hasattr(msg_object, 'message'):
            print("{}: {}".format(msg_object.user_id, msg_object.message))

    a.on_message(on_message)
    a.send('@liweiong', 'hi')