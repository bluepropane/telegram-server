import db

def process_response(msg):
    """
    AI conversation logic goes here.
    @param msg: Message object. sender details are stored
                in msg.sender, while receiver details (the bot) are stored in msg.receiver.
                Message text content (from the sender) is stored in msg.text
                See below for an example.
    """
    db.insert_one('chat_history', {
        'text': msg.sender.text
    })
    if msg.text.lower() == 'hi':
        response_message = 'Hi there {.first_name}!'.format(msg.sender)
    else:
        response_message = 'Sorry, I didn\'t quite get you.'

    self.send('@{}'.format(msg.sender.username), response_message)