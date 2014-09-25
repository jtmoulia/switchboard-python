#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
This Switchboard worker delivers emails to Lamson.
"""

__author__ = u"Thomas Moulia <jtmoulia@pocketknife.io>"
__copyright__ = u"Copyright © 2014, ThusFresh Inc All rights reserved."


import switchboard
from lamson import server

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class LamsonWorker(switchboard.Fetcher):

    def __init__(self, lamson_host='127.0.0.1', lamson_port=8823, lamson_debug=0,
                 *args, **kwargs):
        super(LamsonWorker, self).__init__(*args, **kwargs)
        self._relay = server.Relay(lamson_host, port=lamson_port, debug=lamson_debug)

    def opened(self):
        """Connect to the websocket, and ensure the account is connected and
        the INBOX is being watched, and then start watchingAll.
        """
        def post_setup((cmds, resps)):
            """Post setup callback."""
            logger.info("Setup complete, listening...")

        self.send_cmds(('watchAll', {})).then(post_setup)

    def received_new(self, msg):
        """
        As new messages arrive, deliver them to the lamson relay.
        """
        logger.info("Receiving msg, delivering to Lamson...")
        logger.debug("Relaying msg to lamson: From: %s, To: %s",
                     msg['From'], msg['To'])
        self._relay.deliver(msg)


def main(url, lamson_host, lamson_port, lamson_debug):
    """
    Create, connect, and block on the Lamson worker.
    """
    try:
        worker = LamsonWorker(url=url,
                              lamson_host=lamson_host,
                              lamson_port=lamson_port,
                              lamson_debug=lamson_debug)
        worker.connect()
        worker.run_forever()
    except KeyboardInterrupt:
        worker.close()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Switchboard -> Lamson Worker")
    parser.add_argument('--url', default= "ws://192.168.50.2:8080/workers",
                        help="switchboard's websocket url")
    parser.add_argument('--host', default='127.0.0.1',
                        help="lamson's host")
    parser.add_argument('--port', default=8823,
                        help="lamson's port")
    parser.add_argument('--debug', default=0, help="lamson's debug level")
    args = parser.parse_args()
    main(args.url, args.host, args.port, args.debug)
