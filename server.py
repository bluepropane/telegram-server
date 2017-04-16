from bottle import run, route, request, response
from telegram_controllers import TelegramController


def get_params():
    """
    Parse the request params and context params from bottle request object and return two dictionaries
    """

@route('/', method=['GET'],)
def health():
    return 'healthy'


@route('/telegram', method=['GET', 'POST'])
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
                request_params.update(field.dict)

        if request.json:
            request_params.update(request.json)

        print(request_params)
        func = getattr(TelegramController(), request.method.lower())
        return func(request_params)
    except Exception as err:
        print('%r' % err)
        response.status = 500
        return 'Internal Server Error.'


def main():
    run(server='tornado', host='localhost', port=80)


if __name__ == '__main__':
    main()