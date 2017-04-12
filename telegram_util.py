import socket
import sys


class TelegramTCPHelper(object):

    TELEGRAM_MTP_ADDR_HOST = {
        'dev': '149.154.167.40',
        'prod': '149.154.167.50'
    }
    TELEGRAM_MTP_ADDR_PORT = 443


    def __init__(self, host='localhost', port=10000, env='dev'):
        self.port = port
        self.host = host
        self.receiver = None
        self.sender = None
        self.env = env
        self.observers = []
        # self._init_server()
        # self._init_sender()

    def _init_server(self):
        # Create a TCP/IP socket
        self.receiver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind the socket to the port
        print 'starting up %s on %s port %s' % (TelegramTCPHelper.__name__, self.host, self.port)
        self.receiver.bind((self.host, self.port))

    def _init_sender(self):
        self.sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect the socket to the port where the server is listening
        telegram_mtp_addr = (self.TELEGRAM_MTP_ADDR_HOST[self.env], self.TELEGRAM_MTP_ADDR_PORT)
        print >>sys.stderr, 'connecting to Telegram MTProto server: %s:%s' % telegram_mtp_addr
        self.sender.connect((self.host, self.port))

    def listen(self):
        """
        Listen for incoming connections
        """
        if self.receiver is None:
            self._init_server()

        self.receiver.listen(1)

        try:
            while True:
                # Wait for a connection
                print >>sys.stderr, 'waiting for a connection'
                connection, client_address = self.receiver.accept()
                self._on_connection(connection, client_address)

        finally:
            self.receiver.close()

    def _on_connection(self, connection, client_address):
        try:
            print >>sys.stderr, 'connection from', client_address

            # Receive the data in small chunks and retransmit it
            while True:
                data = connection.recv(16)
                print >>sys.stderr, 'received "%s"' % data
                if data:
                    print >>sys.stderr, 'sending data back to the client'
                    connection.sendall(data)
                else:
                    print >>sys.stderr, 'no more data from', client_address
                    break
                
        finally:
            # Clean up the connection
            connection.close()

    def on_connection(self, callback):
        """
        Register observer for callback when message is received
        @param callback
        """
        self.observers.append(callback)        

    def send(self, message='test message'):
        try:
            # Send data
            print >>sys.stderr, 'sending "%s"' % message
            self.sender.sendall(message)

            # Look for the response
            amount_received = 0
            amount_expected = len(message)
            
            while amount_received < amount_expected:
                data = self.sender.recv(16)
                amount_received += len(data)
                print >>sys.stderr, 'received "%s"' % data

        finally:
            print >>sys.stderr, 'closing socket'
            self.sender.close()