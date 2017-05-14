from bottle import Bottle, request, response
from telegram_controllers import TelegramController
from event_controllers import EventController
from broadcast_controllers import BroadcastController
import telegram_util
import logging

logging.basicConfig(filename='log/access-error.log',level=logging.INFO)
LOGGER = logging.getLogger(__name__)

SERVICES = {
    'telegram': TelegramController,
    'event': EventController,
    'broadcast': BroadcastController
}

# call it once here to load it up
telegram_util.get_instance()

app = Bottle()

@app.route('/', method=['GET'],)
def health():
    return 'healthy'


@app.route('/<service>', method=['GET', 'POST'])
def service_handler(service):
    # print('Called {method} {url} with data = {form}, query = {query}, params = {params}'.format({
    #   'method': request.method,
    #   'url': request.url,
    #   'form': request.forms.dict,
    #   'query': request.query.dict,
    #   'params': request.params
    # }))
    response.status = 200
    request_params = {}

    for field_type in ['query', 'forms']:
        field = getattr(request, field_type)
        if field:
            field_value = {k: v[0] for k, v in field.dict.items()}
            print('%s: %s' % (field_type, field_value))
            request_params.update(field_value)

    if request.json:
        print('json: %s' % request.json)
        request_params.update(request.json)

    print(request_params)
    service = SERVICES[service]
    func = getattr(service(), request.method.lower())
    res = func(request_params, response)
    return res


def main(port=8080):
    app.run(server='tornado', host='localhost', port=port)


if __name__ == '__main__':
    main()