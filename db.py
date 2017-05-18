from pymysql.err import InterfaceError, OperationalError
import pymysql.cursors
import json
import atexit
import redis as r
import logging

LOGGER = logging.getLogger(__name__)

config = json.load(open('creds/db.json'))

class ConnectionPool():
    """
    Usage:
        conn_pool = nmi_mysql.ConnectionPool(config)
        db = conn_pool.get_connection()
        db.query('SELECT 1', [])
        conn_pool.return_connection(db)
        conn_pool.close()
    """
    def __init__(self, conf=None, max_pool_size=20):
        self.conf = conf
        self.max_pool_size = max_pool_size
        self.initialize_pool()

    def initialize_pool(self):
        self.pool = Queue(maxsize=self.max_pool_size)
        for _ in range(0, self.max_pool_size):
            self.pool.put_nowait(pymysql.connect(
                                    host=self.conf.get('host'),
                                    user=self.conf.get('user'),
                                    password=self.conf.get('pass'),
                                    port=self.conf.get('port'),
                                    db=self.conf.get('db'),
                                    charset='utf8mb4',
                                    cursorclass=pymysql.cursors.DictCursor))

    def get_connection(self):
        # returns a db instance when one is available else waits until one is
        db = self.pool.get(True)

        # checks if db is still connected because db instance automatically closes when not in used
        if not self.ping(db):
            db.connect()

        return db

    def return_connection(self, db):
        return self.pool.put_nowait(db)

    def close(self):
        while not self.is_empty():
            self.pool.get().close()

    def ping(self, db):
        data = db.query('SELECT 1', [])
        return data

    def get_initialized_connection_pool(self):
        return self.pool

    def is_empty(self):
        return self.pool.empty()

def cleanup():
    if connection:
        connection.close()
        print('Closed connection to db')

atexit.register(cleanup)

def _connect():
    return pymysql.connect(host=config.get('host'),
                             user=config.get('user'),
                             password=config.get('pass'),
                             port=config.get('port'),
                             db=config.get('db'),
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
connection = _connect()

def read(sql, params=None):
    """
    DB read operations. fetchone() will be used if 'LIMIT 1' is present in the query. 
    Otherwise, fetchall() will be used.
    @param {str} sql: SQL querystring
    @param {tuple} params: to be formatted into the SQL querystring
    @return result: {list} and {dict} for fetchall() and fetchone() respectively.
    """
    global connection
    try:
        LOGGER.info('DB: executed {}'.format((sql % params) if params else sql))
        with connection.cursor() as cursor:
            result = None
            cursor.execute(sql, params)
            if 'LIMIT 1' in sql.upper():
                result = cursor.fetchone()
            else:
                result = cursor.fetchall()

            LOGGER.info('---- result: {}'.format(result))
            return result

    except InterfaceError:
        LOGGER.debug('mysql connection closed; re-establishing connection to db')
        connection = _connect()
    except OperationalError:
        LOGGER.debug('my connection broken; re-establishing connection to db')
        connection = _connect()
    except Exception as err:
        LOGGER.error('DB err: %r' % err)


def write(sql, params=None):
    """
    DB write operations.
    @param {str} sql: SQL querystring
    @param {tuple} params: to be formatted into the SQL querystring
    @return result: {list} and {dict} for fetchall() and fetchone() respectively.
    """
    global connection
    try:
        with connection.cursor() as cursor:
            # Create a new record
            cursor.execute(sql, params)

            LOGGER.info('DB: executed {}'.format((sql % params) if params else sql))

        connection.commit()
    except InterfaceError:
        LOGGER.debug('re-establishing connection to db')
        connection = _connect()
    except OperationalError:
        LOGGER.debug('re-establishing connection to db')
        connection = _connect()
    except Exception as err:
        LOGGER.error('DB err: %r' % err)

def insert_one(table_name, column_pairs):
    """
    Basic helper function to insert a new row into db.
    @param {str} table_name: name of table to insert into. WARNING: unsafe operation: should not
            be arbitrary user input.
    @param {dict} column_pairs: a key-value pair representing the columns and their
            corresponding values in a row. WARNING: keys should not be arbitrary input, only values.
    """
    sql = (
        """
        INSERT INTO {table_name} ({columns}) VALUES (%(values)s)
        """.format(**{
            'table_name': table_name,
            'columns': '{}'.format(','.join([str(key) for key in column_pairs.keys()])),
        })
        )

    params = {
        'values': ','.join([str(val) for val in column_pairs.values()]),
    }
    write(sql, params)

redis = r.StrictRedis(host='localhost', port=6379, db=0)