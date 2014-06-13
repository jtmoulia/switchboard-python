#!/usr/bin/env python
# -*- coding: utf-8 -*-

import apns
import switchboard
import argparse

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

HOSTS = {'localhost': 'ws://127.0.0.1:8080/workers'}

## These are example parameters, replace them with real values
# The APNS hex token to send push notifications to.
HEX_TOKEN = 'b5bb9d8014a0f9b1d61e21e796d78dccdf1352f23cd32812f4850b87'

# The arguments used to start the APNS connection
APNS_ARGS = {
    'use_sandbox': True,
    'cert_file': 'cert.pem',
    'key_file': 'key.pem'}

# Flip this to True to allow the worker to send push notifications
SEND_APNS = False


class APNSWorker(switchboard.Client):
    """A Switchboard worker that will listen for new emails across all
    accounts. For each new email it wil fetch additional information,
    form it into a push notification, and send it to the client.
    """

    def __init__(self, *args, **kwargs):
        super(APNSWorker, self).__init__(*args, **kwargs)
        self._apns = apns.APNs(**APNS_ARGS)

    def connect(self):
        """Connect to the websocket, and ensure the account is connected and
        the INBOX is being watched, and then start watchingAll.
        """
        super(APNSWorker, self).connect()

        def post_setup((cmds, resps)):
            """Post setup callback."""
            logger.info("Setup complete, listening...")

        self.send_cmds(('watchAll', {})).then(post_setup)


    def received_unsolicited(self, resps):
        def post_fetch((cmds, resps)):
            """Post fetch callback."""
            for msg in resps[0][1]['list']:
                logger.debug("Preparing msg to send: %s", msg)
                from1 = msg['from'][0]
                from_name = from1.get('name') or from1.get('email', '<unknown>')
                notification = "%s - %s" % (from_name, msg['subject'])
                payload = apns.Payload(notification, sound='default', badge=1)
                if SEND_APNS:
                    logger.debug("sending push notification: %s", payload)
                    self._apns.gateway_server.send_notification(TOKEN_HEX, payload)
                else:
                    logger.info("-- push notification would be sent: %s --", payload)

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



def main(url):
    """Create, connect, and block on the listener worker."""
    try:
        worker = APNSWorker(url)
        worker.connect()
        worker.run_forever()
    except KeyboardInterrupt:
        worker.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Loop echo listener")
    parser.add_argument("host")
    args = parser.parse_args()
    main(HOSTS[args.host])
