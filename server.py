from bottle import run, route, request, response
from telegram_controllers import TelegramController



@route('/', method=['GET'],)
def health():
	return 'healthy'


@route('/telegram', method=['GET', 'POST'])
def telegram():
	# print('Called {method} {url} with data = {form}, query = {query}, params = {params}'.format({
	# 	'method': request.method,
	# 	'url': request.url,
	# 	'form': request.forms.dict,
	# 	'query': request.query.dict,
	# 	'params': request.params
	# }))
	try:
		response.status = 200
		print(request.query.dict)
		func = getattr(TelegramController(), request.method.lower())
		return func(request.query)
	except Exception as err:
		print('%r' % err)
		response.status = 500
		return 'Internal Server Error.'


def main():
	run(server='tornado', host='localhost', port=8080)


if __name__ == '__main__':
	main()