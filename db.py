import pymysql.cursors


# Connect to the database
connection = pymysql.connect(host='ec2-34-209-104-246.us-west-2.compute.amazonaws.com',
                             user='heyAI',
                             password='heyAI',
                             db='HeyAI',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

def fetch_one(sql, params):
    try:
        # with connection.cursor() as cursor:
        #     # Create a new record
        #     cursor.execute(sql, ('webmaster@python.org', 'very-secret'))

        # # connection is not autocommit by default. So you must commit to save
        # # your changes.
        # connection.commit()

        with connection.cursor() as cursor:
            # Read a single record
            cursor.execute(sql, params)
            result = cursor.fetchone()
            print('DB: executed {} ---- result: {}'.format(sql, result))
            return result
    finally:
        connection.close()

def fetch_one(sql, params=None):
    _fetch(sql, params)

def fetch_all():