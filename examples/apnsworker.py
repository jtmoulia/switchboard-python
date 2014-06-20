#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
APNSWorker is a Switchboard worker that collects incoming emails,
uses them to create a push notification, and then sends them to
an iOS device.

    ./apnsworker.py --help
"""

__author__ = u"Thomas Moulia <jtmoulia@pocketknife.io>"
__copyright__ = u"Copyright © 2014, ThusFresh, Inc. All rights reserved."


import apns
import switchboard
import argparse

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ACCOUNT = 'mail.dispatch.test@gmail.com'
CONN_SPEC = {'host': 'imap.gmail.com',
             'port': 993,
             'auth': {
                 'type': 'plain',
                 'username': ACCOUNT,
                 'password': 'i>V99JuMVEs;'}};


class APNSWorker(switchboard.Client):
    """A Switchboard worker that will listen for new emails across all
    accounts. For each new email it wil fetch additional information,
    form it into a push notification, and send it to the client.
    """

    def __init__(self, cert, key, pushtoken=None, use_sandbox=True, *args, **kwargs):
        super(APNSWorker, self).__init__(*args, **kwargs)
        self._pushtoken = pushtoken
        self._apns = apns.APNs(use_sandbox=use_sandbox, cert_file=cert, key_file=key)

    def opened(self):
        """Connect to the websocket, and ensure the account is connected and
        the INBOX is being watched, and then start watchingAll.
        """
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
            try:
                for msg in resps[0][1]['list']:
                    logger.debug("Preparing msg to send: %s", msg)
                    from1 = msg['from'][0]
                    from_name = from1.get('name') or from1.get('email', '<unknown>')
                    notification = "%s - %s" % (from_name, msg['subject'])
                    payload = apns.Payload(notification, sound='default', badge=1)
                    if self._pushtoken:
                        logger.info("Sending push notification: %s", payload)
                        try:
                            self._apns.gateway_server.send_notification(
                                self._pushtoken, payload)
                        except Exception as e:
                            logger.error("Error sending push notification: %s", e)
                            raise
                    else:
                        logger.info("-- push notification would be sent: %s --", payload)
            except Exception as e:
                logger.error("Error: %s", e)
                raise

        for resp in resps:
            if resp[0] == 'newMessage':
                args = resp[1]
                promise = self.send_cmds(('getMessages',
                                          {'account': args['account'],
                                           'ids': [args['messageId']],
                                           'properties': ['subject', 'from']}))
                promise.then(post_fetch)
            else:
                logger.warning("Unknown unsolicted response: %s", response)



def main(cert, key, pushtoken, url):
    """Create, connect, and block on the listener worker."""
    try:
        worker = APNSWorker(cert=cert, key=key, pushtoken=pushtoken, url=url)
        worker.connect()
        worker.run_forever()
    except KeyboardInterrupt:
        worker.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="APNS Worker")
    parser.add_argument("--cert", default="cert.pem",
                        help="the APNS public certificate")
    parser.add_argument("--key", default="key.pem",
                        help="the APNS private key")
    parser.add_argument("--pushtoken", default=None,
                        help="the push token to send emails to")
    parser.add_argument("--url", default="ws://127.0.0.1:8080/workers",
                        help="the url of the worker websocket interface")
    args = parser.parse_args()
    main(args.cert, args.key, args.pushtoken, args.url)
