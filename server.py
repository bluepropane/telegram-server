from bottle import Bottle, request, response
from telegram_controllers import TelegramController
import logging


LOGGER = logging.getLogger(__name__)

# set up the logger
LOGGER.setLevel(logging.INFO)
file_handler = logging.FileHandler('log/main-process.log')
file_handler.setLevel(logging.DEBUG)
LOGGER.addHandler(file_handler)

def log_to_logger(fn):
    '''
    Wrap a Bottle request so that a log line is emitted after it's handled.
    (This decorator can be extended to take the desired logger as a param.)
    '''
    @wraps(fn)
    def _log_to_logger(*args, **kwargs):
        request_time = datetime.now()
        actual_response = fn(*args, **kwargs)
        # modify this to log exactly what you need:
        LOGGER.info('%s %s %s %s %s' % (request.remote_addr,
                                        request_time,
                                        request.method,
                                        request.url,
                                        response.status))
        return actual_response
    return _log_to_logger

app = Bottle()
app.install(log_to_logger)

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