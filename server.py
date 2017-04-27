from bottle import Bottle, request, response
from telegram_controllers import TelegramController
import telegram_util
import logging

logging.basicConfig(filename='example.log',level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)


telegram_ai = telegram_util.get_instance()
telegram_ai.start_receiver()
telegram_ai.start_ai()

app = Bottle()

@app.route('/', method=['GET'],)
def health():
    return 'healthy'


@app.route('/telegram', method=['GET', 'POST'])
def telegram():
    # print('Called {method} {url} with data = {form}, query = {query}, params = {params}'.format({
    #   'method': request.method,
    #   'url': request.url,
    #   'form': request.forms.dict,
    #   'query': request.query.dict,
    #   'params': request.params
    # }))
    try:
        response.status = 200
        request_params = {}

        for field_type in ['query', 'forms']:
            field = getattr(request, field_type)
            if field:
                print('%s: %s' % (field_type, field.dict))
                request_params.update(field.dict)

        if request.json:
            print('json: %s' % request.json)
            request_params.update(request.json)

        print(request_params)
        func = getattr(TelegramController(), request.method.lower())
        return func(request_params, response)
    except Exception as err:
        print('%r' % err)
        response.status = 500
        return 'Internal Server Error.'


def main(port=8080):
    app.run(server='tornado', host='localhost', port=port)


if __name__ == '__main__':
    main()