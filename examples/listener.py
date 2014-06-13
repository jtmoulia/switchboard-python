#!/usr/bin/env python

import switchboard
import thread
import email

import argparse
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


HOSTS = {'localhost': 'ws://127.0.0.1:8080/workers'}
ACCOUNT = 'mail.dispatch.test@gmail.com'
CONN_SPEC = {'host': 'imap.gmail.com',
             'port': 993,
             'auth': {
                 'type': 'plain',
                 'username': ACCOUNT,
                 'password': 'i>V99JuMVEs;'}};


class ListenerWorker(switchboard.Client):
    """A basic Switchboard worker that will listen for new email
    notifications.  When it receives a notification, it fetches the
    raw email from Switchboard and parses it using the email module.
    """


    def connect(self):
        """Connect to the websocket, and ensure the account is connected and
        the INBOX is being watched, and then start watchingAll.
        """
        super(ListenerWorker, self).connect()

        def post_setup((cmds, resps)):
            """Post setup callback."""
            logger.info("Setup complete, listening...")

        self.send_cmds(('connect', CONN_SPEC),
                       ('watchMailboxes', {'account': ACCOUNT,
                                           'list': ['INBOX']}),
                       ('watchAll', {})).then(post_setup)


    def received_unsolicited(self, resps):
        def post_fetch((cmds, resps)):
            """Post fetch callback."""
            for raw_msg in resps[0][1]['list']:
                msg = email.message_from_string(raw_msg['raw'])
                logger.info("Subject: %s, From: %s, To: %s",
                            msg['subject'], msg['from'], msg['to'])

        for resp in resps:
            if resp[0] == 'newMessage':
                args = resp[1]
                self.send_cmds(('getMessages',
                                {'account': args['account'],
                                 'ids': [args['messageId']],
                                 'properties': ['raw']})).then(post_fetch)

            else:
                logger.warning("Unknown unsolicted response: %s", response)



def main(url):
    """Create, connect, and block on the listener worker."""
    try:
        listener = ListenerWorker(url)
        listener.connect()
        listener.run_forever()
    except KeyboardInterrupt:
        listener.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Loop echo listener")
    parser.add_argument("--host", default="localhost")
    args = parser.parse_args()
    main(HOSTS[args.host])
