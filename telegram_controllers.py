from telegram_models import TelegramUserAccount
import telegram_util


class TelegramController(object):

    def post(self, request_params):
        """
        This endpoint is called for initiating the authorization flow.
        @param request_params: should contain an 'type' paramter. 'onboard' is for
                the initialization of the flow, while 'code' is for verifying the authorization code.
        """
        auth_type = request_params.get('type')
        if auth_type == 'onboard':
            phone_number = request_params.get('phone')
            telegram_user = TelegramUserAccount(phone_number, user_phone=None)

        return {}

    def _sanitize_phone_number(self, number):
        """
        Take away the leading '+' for standardization. Just add it back if needed.
        @param number: phone number
        """
        if number[0] == '+':
            number = number[1:]

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